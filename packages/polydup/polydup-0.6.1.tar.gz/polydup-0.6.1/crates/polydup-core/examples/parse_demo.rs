//! Demo: Parsing functions from Rust, Python, and JavaScript code

use dupe_core::{extract_javascript_functions, extract_python_functions, extract_rust_functions};

fn main() -> anyhow::Result<()> {
    println!("=== PolyDup Function Parsing Demo ===\n");

    // Rust example
    let rust_code = r#"
fn hello_world() {
    println!("Hello, world!");
}

fn add(a: i32, b: i32) -> i32 {
    a + b
}

impl Calculator {
    fn multiply(&self, x: i32, y: i32) -> i32 {
        x * y
    }
}
"#;

    println!("📦 Rust Functions:");
    let rust_funcs = extract_rust_functions(rust_code)?;
    for func in &rust_funcs {
        println!(
            "  - {} (bytes: {}..{})",
            func.name.as_deref().unwrap_or("<anonymous>"),
            func.start_byte,
            func.end_byte
        );
    }
    println!("  Total: {} functions\n", rust_funcs.len());

    // Python example
    let python_code = r#"
def greet(name):
    return f"Hello, {name}!"

def calculate_sum(numbers):
    return sum(numbers)

class Math:
    def divide(self, a, b):
        return a / b
"#;

    println!("🐍 Python Functions:");
    let python_funcs = extract_python_functions(python_code)?;
    for func in &python_funcs {
        println!(
            "  - {} (bytes: {}..{})",
            func.name.as_deref().unwrap_or("<anonymous>"),
            func.start_byte,
            func.end_byte
        );
    }
    println!("  Total: {} functions\n", python_funcs.len());

    // JavaScript example
    let js_code = r#"
function sayHello() {
    console.log("Hello!");
}

const add = (a, b) => {
    return a + b;
};

class Calculator {
    multiply(x, y) {
        return x * y;
    }
}
"#;

    println!("🟨 JavaScript Functions:");
    let js_funcs = extract_javascript_functions(js_code)?;
    for func in &js_funcs {
        println!(
            "  - {} (bytes: {}..{})",
            func.name.as_deref().unwrap_or("<anonymous>"),
            func.start_byte,
            func.end_byte
        );
    }
    println!("  Total: {} functions\n", js_funcs.len());

    println!("✅ Parsing complete!");

    Ok(())
}
