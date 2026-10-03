# 贡献与发布

所有修改通过功能分支、PR 和 CI，获得维护者确认后合并。每个 Rust 文件不超过 200 行，测试放在 tests/。

独立克隆后执行 `cargo fmt --all -- --check`、`cargo test --locked`、`cargo clippy --all-targets --locked -- -D warnings` 和 `RUSTDOCFLAGS="-D warnings" cargo doc --no-deps --locked`。

版本与 dameng-cli 独立管理。修改本仓库 Cargo.toml、Cargo.lock（插件还需同步 dm-plugin.toml），PR 合并确认后在合并提交创建对应 vX.Y.Z 标签。Release workflow 先运行 CI。

GitHub Release 提供九个平台的插件归档及 SHA-256（x86_64/ARM64 GNU 与 musl Linux、ARMv7 GNU Linux、Apple Silicon 与 Intel macOS、x86_64 与 ARM64 Windows），GNU Linux 保持 glibc 2.28 基线并检查符号与运行，同时发布宿主 Git 仓库安装方式所需的原始二进制及 SHA-256。musl 仅发布独立目标归档，避免覆盖同名 GNU 二进制。SDK 使用独立仓库的固定提交；其余工具代码在本仓库的 src/support/ 内维护。不需要宿主目录或其他插件仓库。SDK 发布 crates.io 后可通过 PR 切换到 registry 依赖。
