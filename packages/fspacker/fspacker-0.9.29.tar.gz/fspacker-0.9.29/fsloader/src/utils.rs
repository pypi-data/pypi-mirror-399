use std::fs;
use std::io::{BufRead, BufReader};
use std::path::Path;
use std::process::{Command, Stdio};

pub fn find_entry_files() -> Vec<String> {
    let current_dir = Path::new(".");
    let mut entry_files = Vec::new();

    if let Ok(entries) = fs::read_dir(current_dir) {
        for entry in entries {
            if let Ok(entry) = entry {
                let path = entry.path();
                if path.is_file() && path.extension().and_then(|e| e.to_str()) == Some("int") {
                    entry_files.push(path.to_string_lossy().into_owned());
                }
            }
        }
    }
    entry_files
}

pub fn run_python_script(script_path: &str) {
    let python_path = if cfg!(target_os = "windows") {
        if cfg!(feature = "gui") {
            Path::new("runtime/pythonw.exe")
        } else {
            Path::new("runtime/python.exe")
        }
    } else {
        Path::new("/usr/bin/python3")
    };

    let mut child = Command::new(python_path)
        .arg(script_path)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("启动Python失败");

    // 异步读取输出流
    let stdout = BufReader::new(child.stdout.take().unwrap());
    let stderr = BufReader::new(child.stderr.take().unwrap());

    // 输出处理线程
    let handle = std::thread::spawn(move || {
        for line in stdout.lines() {
            match line {
                Ok(content) => println!("输出: {}", content),
                Err(_) => break, // 处理读取错误时优雅退出
            }
        }
        for line in stderr.lines() {
            match line {
                Ok(content) => eprintln!("信息: {}", content),
                Err(_) => break, // 处理读取错误时优雅退出
            }
        }
    });

    let _status = child.wait().expect("进程未正常退出");

    // 安全地等待线程结束
    if let Err(e) = handle.join() {
        eprintln!("线程执行出错: {:?}", e);
    }
}
