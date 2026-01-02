use linear_regression::{LinearRegressionResult, do_linear_regression};
use std::fs::File;
use std::io::{BufRead, BufReader, Write};
use std::path::{Path, PathBuf};
use std::{env, process};

fn main() {
    let args: Vec<String> = env::args().collect();
    run(&args);
}

fn run(args: &[String]) {
    let (input_file, output_path) = parse_args(args);
    println!("Input file: {}", input_file.display());
    println!("Output file: {}", output_path.display());
    let input_data = read_input_file(&input_file);
    println!("Read {} data points", input_data.len());
    let results = do_linear_regression(&input_data);
    write_results(&output_path, &results);
    println!("Done");
}

/// Parses command line arguments and returns input and output file paths.
fn parse_args(args: &[String]) -> (PathBuf, PathBuf) {
    if args.len() != 3 {
        eprintln!("Usage: linear_regression <input_file> <output_file>");
        process::exit(1);
    }

    let input = &args[1];
    let output = &args[2];

    let input_path = PathBuf::from(input);
    if input_path.extension() != Some(std::ffi::OsStr::new("tsv")) {
        panic!("Input file must be a .tsv file");
    }
    if !input_path.exists() {
        panic!("Input file does not exist");
    }

    if !output.ends_with(".tsv") {
        panic!("Output file must be a .tsv file");
    }
    let output_path = PathBuf::from(output);
    if output_path.exists() {
        panic!("Output file already exists");
    }

    (input_path, output_path)
}

/// Reads the input TSV file and returns a vector of (x, y) data points.
/// Panics if
/// - the file cannot be read
/// - any line does not have exactly two tab-separated values
/// - any value cannot be parsed as f64
/// - any value is not finite
fn read_input_file(path: &Path) -> Vec<f64> {
    let file = match File::open(path) {
        Ok(f) => f,
        Err(_) => panic!("Cannot read {}", path.display()),
    };
    let reader = BufReader::new(file);
    let mut data = Vec::new();
    for (line_number, line) in reader.lines().enumerate() {
        let line_number = line_number + 1; // Make line numbers 1-based
        let line = match line {
            Ok(l) => l,
            Err(_) => panic!("Cannot read line {line_number}"),
        };
        let parts: Vec<&str> = line.split('\t').collect();
        if parts.len() != 2 {
            panic!("Line {line_number}: expected 2 values, got {}", parts.len());
        }
        let mut xy = [0.0f64, 0.0f64];
        for (i, part) in parts.iter().enumerate() {
            let value: f64 = match part.parse() {
                Ok(v) => v,
                Err(_) => panic!("Line {line_number}: cannot parse value '{}'", part),
            };
            if !value.is_finite() {
                panic!("Line {line_number}: value '{}' is not finite", part);
            }
            xy[i] = value;
        }
        data.push(xy);
    }
    if data.len() <= 2 {
        panic!("At least 3 data points are required for linear regression");
    }
    data.as_flattened().to_vec()
}

fn write_results(output_path: &PathBuf, results: &LinearRegressionResult) {
    let mut file = match File::create(output_path) {
        Ok(f) => f,
        Err(_) => panic!("Cannot create output file {}", output_path.display()),
    };
    for (key, value) in results.iter() {
        writeln!(file, "{}\t{}", key, value).unwrap();
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    // Learning notes:
    // use crate::*; // The same as using super::*;
    // use linear_regression::*;  // If there is code in src/lib.rs, this will bring them in.
    use tempfile::tempdir;

    #[test]
    fn test_parse_args_ok() {
        let tmp = tempdir().unwrap().keep();
        let input_path = tmp.join("lr_input.tsv");
        let output_path = tmp.join("lr_output.tsv");
        std::fs::write(&input_path, "1\t2\n").unwrap();
        if output_path.exists() {
            std::fs::remove_file(&output_path).unwrap();
        }

        let args = vec![
            "prog".into(),
            input_path.to_string_lossy().into(),
            output_path.to_string_lossy().into(),
        ];
        let (inp, outp) = parse_args(&args);
        assert_eq!(inp, input_path);
        assert_eq!(outp, output_path);
    }

    #[test]
    #[should_panic(expected = "Input file does not exist")]
    fn test_parse_args_missing_input() {
        let tmp = tempdir().unwrap().keep();
        let missing_input = tmp.join("definitely_missing_input.tsv");
        assert!(!missing_input.exists());
        let output_path = tmp.join("lr_output2.tsv");
        if output_path.exists() {
            std::fs::remove_file(&output_path).unwrap();
        }

        let args = vec![
            "prog".into(),
            missing_input.to_string_lossy().into(),
            output_path.to_string_lossy().into(),
        ];
        // Should panic
        let _ = parse_args(&args);
    }

    // ---- Tests for read_input_file ----
    #[test]
    fn test_read_input_file_ok() {
        let tmp = std::env::temp_dir();
        let path = tmp.join("read_ok.tsv");
        std::fs::write(&path, "1\t2\n3.5\t4.5\n-1\t0\n").unwrap();
        let data = read_input_file(&path);
        assert_eq!(data.len(), 6);
        assert_eq!(data, vec![1.0, 2.0, 3.5, 4.5, -1.0, 0.0]);
    }

    #[test]
    #[should_panic(expected = "expected 2 values")]
    fn test_read_input_file_bad_columns() {
        let tmp = std::env::temp_dir();
        let path = tmp.join("read_bad_cols.tsv");
        std::fs::write(&path, "1\t2\t3\n").unwrap();
        let _ = read_input_file(&path);
    }

    #[test]
    #[should_panic(expected = "cannot parse value 'abc'")]
    fn test_read_input_file_parse_error() {
        let tmp = std::env::temp_dir();
        let path = tmp.join("read_parse_err.tsv");
        std::fs::write(&path, "abc\t2\n").unwrap();
        let _ = read_input_file(&path);
    }

    #[test]
    #[should_panic(expected = "is not finite")]
    fn test_read_input_file_not_finite() {
        let tmp = std::env::temp_dir();
        let path = tmp.join("read_not_finite.tsv");
        std::fs::write(&path, "NaN\t2\n").unwrap();
        let _ = read_input_file(&path);
    }

    #[test]
    #[should_panic(expected = "Cannot read")]
    fn test_read_input_file_missing_file() {
        let tmp = std::env::temp_dir();
        let path = tmp.join("definitely_missing_lr.tsv");
        assert!(!path.exists());
        let _ = read_input_file(&path);
    }

    #[test]
    fn test_run_simple_case() {
        // Create temp input/output files using simple perfect linear data y = x + 1
        let tmp_dir = tempfile::tempdir().unwrap();
        let input_path = tmp_dir.path().join("run_input.tsv");
        let output_path = tmp_dir.path().join("run_output.tsv");
        std::fs::write(&input_path, "1\t2\n2\t3\n3\t4\n").unwrap();
        assert!(!output_path.exists());

        let args = vec![
            "prog".to_string(),
            input_path.to_string_lossy().into(),
            output_path.to_string_lossy().into(),
        ];
        run(&args);

        assert!(output_path.exists(), "run() did not create output file");
        let contents = std::fs::read_to_string(&output_path).unwrap();
        let mut beta_0_found = false;
        let mut beta_1_found = false;
        for line in contents.lines() {
            if let Some(rest) = line.strip_prefix("beta_0\t") {
                let v: f64 = rest.parse().unwrap();
                assert!((v - 1.0).abs() < 1e-12, "beta_0 expected 1.0 got {v}");
                beta_0_found = true;
            }
            if let Some(rest) = line.strip_prefix("beta_1\t") {
                let v: f64 = rest.parse().unwrap();
                assert!((v - 1.0).abs() < 1e-12, "beta_1 expected 1.0 got {v}");
                beta_1_found = true;
            }
        }
        assert!(beta_0_found, "beta_0 line not found in output");
        assert!(beta_1_found, "beta_1 line not found in output");
    }
}
