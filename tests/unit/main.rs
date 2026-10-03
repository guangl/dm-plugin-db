//! Unit tests for the database plugin: storage, configuration, prompts and
//! command dispatch. The driver behind "dm db test" and "dm db exec" is still a
//! placeholder, so these tests drive the commands with a scripted fake driver
//! and never need a database. The connection export/import tests live in the
//! tests/export target next to these modules.

mod commands;
mod common;
mod config;
mod connection_string;
mod crypto;
mod exec_command;
mod fake_driver;
mod plugin;
mod prompts;
mod sql;
mod store;
mod support_completion;
mod support_config;
mod support_interaction;
mod support_resources;
mod support_secrets;
mod test_command;

mod usability;
