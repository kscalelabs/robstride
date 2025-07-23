use bytemuck::{Pod, Zeroable};
use std::io;
use std::os::unix::io::{AsRawFd, RawFd};
use tokio::io::unix::AsyncFd;

pub const CAN_MAX_DLEN: usize = 8;

/// CAN frame structure taken from linux/include/uapi/linuxcan.h
#[derive(Debug, Default, Clone, Copy, PartialEq, Pod, Zeroable)]
#[repr(C, packed)]
pub struct CanFrame {
    pub can_id: u32,
    pub len: u8,
    pub pad: u8,
    pub res0: u8,
    pub len8_dlc: u8,
    pub can_data: [u8; CAN_MAX_DLEN],
}

impl From<CanFrame> for [u8; 16] {
    fn from(frame: CanFrame) -> Self {
        bytemuck::cast(frame)
    }
}

impl From<[u8; 16]> for CanFrame {
    fn from(bytes: [u8; 16]) -> Self {
        bytemuck::cast(bytes)
    }
}

/// CAN interface for communicating with actuators
/// Follows the original firmware pattern using AsyncFd + libc calls
pub struct CanInterface {
    async_fd: AsyncFd<RawFd>,
    interface_name: String,
}

impl CanInterface {
    pub fn new(interface_name: &str) -> crate::Result<Self> {
        // Create socket using socket2
        let socket = socket2::Socket::new(
            socket2::Domain::from(libc::AF_CAN),
            socket2::Type::RAW,
            Some(socket2::Protocol::from(libc::CAN_RAW)),
        )?;

        let if_index = unsafe {
            let cstr = std::ffi::CString::new(interface_name)
                .map_err(|_| crate::RobstrideError::Can("Invalid interface name".into()))?;
            libc::if_nametoindex(cstr.as_ptr())
        };

        if if_index == 0 {
            return Err(crate::RobstrideError::Can(format!(
                "Interface {} not found",
                interface_name
            )));
        }

        let addr = libc::sockaddr_can {
            can_family: libc::AF_CAN as _,
            can_ifindex: if_index as i32,
            can_addr: unsafe { std::mem::zeroed() },
        };

        let mut sockaddr_storage: libc::sockaddr_storage = unsafe { std::mem::zeroed() };
        unsafe {
            std::ptr::copy_nonoverlapping(
                &addr as *const _ as *const u8,
                &mut sockaddr_storage as *mut _ as *mut u8,
                std::mem::size_of::<libc::sockaddr_can>(),
            );
        }

        let sockaddr = unsafe {
            socket2::SockAddr::new(
                sockaddr_storage,
                std::mem::size_of::<libc::sockaddr_can>() as u32,
            )
        };

        socket.bind(&sockaddr)?;
        socket.set_nonblocking(true)?;

        // Get raw fd and wrap in AsyncFd
        let raw_fd = socket.as_raw_fd();
        let async_fd = AsyncFd::new(raw_fd)?;

        // Keep socket alive by forgetting it (AsyncFd owns the fd now)
        std::mem::forget(socket);

        Ok(CanInterface {
            async_fd,
            interface_name: interface_name.to_string(),
        })
    }

    pub async fn send_frame(&self, frame: &CanFrame) -> crate::Result<()> {
        let bytes: [u8; 16] = (*frame).into();

        loop {
            let mut guard = self.async_fd.writable().await?;
            match guard.try_io(|inner| {
                let n = unsafe {
                    libc::write(
                        inner.as_raw_fd(),
                        bytes.as_ptr() as *const libc::c_void,
                        bytes.len(),
                    )
                };
                if n < 0 {
                    Err(io::Error::last_os_error())
                } else {
                    Ok(n as usize)
                }
            }) {
                Ok(Ok(_)) => break,
                Ok(Err(e)) => return Err(e.into()),
                Err(_would_block) => continue,
            }
        }
        Ok(())
    }

    pub async fn recv_frame(&self) -> crate::Result<CanFrame> {
        let mut buffer = [0u8; 16];

        loop {
            let mut guard = self.async_fd.readable().await?;
            match guard.try_io(|inner| {
                let n = unsafe {
                    libc::read(
                        inner.as_raw_fd(),
                        buffer.as_mut_ptr() as *mut libc::c_void,
                        buffer.len(),
                    )
                };
                if n < 0 {
                    Err(io::Error::last_os_error())
                } else if n == 0 {
                    Err(io::Error::new(
                        io::ErrorKind::UnexpectedEof,
                        "Socket closed",
                    ))
                } else {
                    Ok(n as usize)
                }
            }) {
                Ok(Ok(_)) => break,
                Ok(Err(e)) => return Err(e.into()),
                Err(_would_block) => continue,
            }
        }

        Ok(CanFrame::from(buffer))
    }

    pub fn interface_name(&self) -> &str {
        &self.interface_name
    }

    /// Synchronous try_read for compatibility
    pub fn try_read(&self, buf: &mut [u8]) -> io::Result<usize> {
        let n = unsafe {
            libc::read(
                self.async_fd.as_raw_fd(),
                buf.as_mut_ptr() as *mut libc::c_void,
                buf.len(),
            )
        };
        if n < 0 {
            Err(io::Error::last_os_error())
        } else {
            Ok(n as usize)
        }
    }
}
