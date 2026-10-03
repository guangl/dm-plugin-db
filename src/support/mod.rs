//! dm db 插件自带的实现工具：有界读取、十六进制编码、AES-GCM 字节格式、
//! 终端交互、配置展示、诊断报告与补全候选。
//!
//! 这些代码跟随本仓库一起版本化：插件不依赖宿主仓库，也不依赖其他插件
//! 仓库，独立克隆后即可构建。公开的进程协议仍然由 dm-plugin-sdk 定义。

pub mod bounded;
pub mod codec;
pub mod completion;
pub mod config;
pub mod diagnostics;
pub mod interaction;
pub mod private_file;
pub mod secrets;
mod suggestions;
