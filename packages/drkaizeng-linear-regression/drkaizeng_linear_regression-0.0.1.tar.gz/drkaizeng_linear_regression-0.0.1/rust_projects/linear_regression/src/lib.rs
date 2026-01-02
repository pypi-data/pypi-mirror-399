use statrs::distribution::{ContinuousCDF, StudentsT};

macro_rules! iterable_struct {
    ($struct_name:ident<$field_type:ty> { $($field:ident),* $(,)? }) => {
        // Define the struct with all fields of type $field_type
        #[derive(Debug)]
        pub struct $struct_name {
            $(pub $field: $field_type),*
        }

        impl $struct_name {
            // Returns an iterator over (field_name, value) tuples
            pub fn iter(&self) -> impl Iterator<Item = (&'static str, $field_type)>
            where
                $field_type: Copy
            {
                vec![
                    $(
                        (stringify!($field), self.$field)
                    ),*
                ].into_iter()
            }
        }
    };
}

iterable_struct!(LinearRegressionResult<f64> {
    beta_1,
    var_beta_1,
    beta_1_conf_low,
    beta_1_conf_high,
    beta_1_p_value,
    beta_0,
    var_beta_0,
    beta_0_conf_low,
    beta_0_conf_high,
    beta_0_p_value,
    r_squared,
});

/// Perform linear regression on the provided data points.
///
/// IMPORTANT: This is considered a low-level implementation and does not check that the input data
///     slice is non-empty and have an even number of elements.
///
/// # Arguments
///
/// * `data` - A slice of f64 numbers. There should be an even number of elements,
///   where each consecutive pair represents an (x, y) data point.
pub fn do_linear_regression(data: &[f64]) -> LinearRegressionResult {
    let (chunks, _) = data.as_chunks::<2>();
    let n = data.len() as f64 / 2.0;
    let mean_x = chunks.iter().map(|&[x, _]| x).sum::<f64>() / n;
    let mean_y = chunks.iter().map(|&[_, y]| y).sum::<f64>() / n;
    let sum_x_sq = chunks.iter().map(|&[x, _]| x.powi(2)).sum::<f64>();
    let sum_xy = chunks.iter().map(|&[x, y]| x * y).sum::<f64>();
    let beta_1 = (sum_xy - n * mean_x * mean_y) / (sum_x_sq - n * mean_x.powi(2));
    let beta_0 = mean_y - beta_1 * mean_x;
    let bar_y: Vec<f64> = chunks.iter().map(|&[x, _]| beta_0 + beta_1 * x).collect();
    let sigma_sq = chunks
        .iter()
        .map(|&[_, y]| y)
        .zip(bar_y.iter())
        .map(|(y, bar_y)| (y - bar_y).powi(2))
        .sum::<f64>()
        / (n - 2.0);
    let n_var_x = sum_x_sq - n * mean_x.powi(2);
    let var_beta_1 = sigma_sq / n_var_x;
    let var_beta_0 = sigma_sq * (1.0 / n + mean_x.powi(2) / n_var_x);

    let t_dist =
        StudentsT::new(0.0, 1.0, n - 2.0).expect("Failed to create Student's t-distribution");
    let cutoff = t_dist.inverse_cdf(0.975);
    let beta_1_conf_low = beta_1 - cutoff * var_beta_1.sqrt();
    let beta_1_conf_high = beta_1 + cutoff * var_beta_1.sqrt();
    let beta_1_p_value = 2.0 * (1.0 - t_dist.cdf(beta_1.abs() / var_beta_1.sqrt()));

    let beta_0_conf_low = beta_0 - cutoff * var_beta_0.sqrt();
    let beta_0_conf_high = beta_0 + cutoff * var_beta_0.sqrt();
    let beta_0_p_value = 2.0 * (1.0 - t_dist.cdf(beta_0.abs() / var_beta_0.sqrt()));

    let ssr = bar_y.iter().map(|&x| (x - mean_y).powi(2)).sum::<f64>();
    let sst = chunks
        .iter()
        .map(|&[_, y]| (y - mean_y).powi(2))
        .sum::<f64>();
    let r_squared = ssr / sst;

    LinearRegressionResult {
        beta_1,
        var_beta_1,
        beta_1_conf_low,
        beta_1_conf_high,
        beta_1_p_value,
        beta_0,
        var_beta_0,
        beta_0_conf_low,
        beta_0_conf_high,
        beta_0_p_value,
        r_squared,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_do_linear_regression_simple_case() {
        let data = vec![1.0, 2.0, 2.0, 3.0, 3.0, 4.0];
        let results = do_linear_regression(&data);
        assert_eq!(results.beta_1, 1.0);
        assert_eq!(results.var_beta_1, 0.0);
        assert_eq!(results.beta_1_conf_low, 1.0);
        assert_eq!(results.beta_1_conf_high, 1.0);
        assert_eq!(results.beta_1_p_value, 0.0);
        assert_eq!(results.beta_0, 1.0);
        assert_eq!(results.var_beta_0, 0.0);
        assert_eq!(results.beta_0_conf_low, 1.0);
        assert_eq!(results.beta_0_conf_high, 1.0);
        assert_eq!(results.beta_0_p_value, 0.0);
        assert_eq!(results.r_squared, 1.0);
    }

    #[test]
    /// Data from Example 6.2 in Rencher and Schaalje (2008)
    fn test_do_linear_regression_example_6_2() {
        let data = vec![
            [96.0, 95.0],
            [77.0, 80.0],
            [0.0, 0.0],
            [0.0, 0.0],
            [78.0, 79.0],
            [64.0, 77.0],
            [89.0, 72.0],
            [47.0, 66.0],
            [90.0, 98.0],
            [93.0, 90.0],
            [18.0, 0.0],
            [86.0, 95.0],
            [0.0, 35.0],
            [30.0, 50.0],
            [59.0, 72.0],
            [77.0, 55.0],
            [74.0, 75.0],
            [67.0, 66.0],
        ];
        let data = data.as_flattened();
        let results = do_linear_regression(data);

        fn format_f64(value: f64, num_decimal_places: usize, scientific: bool) -> String {
            if scientific {
                format!("{:.1$e}", value, num_decimal_places)
            } else {
                format!("{:.1$}", value, num_decimal_places)
            }
        }
        assert_eq!(format_f64(results.beta_1, 4, false), "0.8726");
        // Difference due to rounding in the book. The \hat{sigma} (i.e. s in the book) is 13.85467
        // sqrt(n_var_x) = 139.7532. These are agree with the book.
        assert_eq!(format_f64(results.var_beta_1, 5, false), "0.00983");
        assert_eq!(format_f64(results.beta_1_conf_low, 4, false), "0.6625");
        assert_eq!(format_f64(results.beta_1_conf_high, 4, false), "1.0828");
        assert_eq!(format_f64(results.beta_1_p_value, 3, true), "1.571e-7");
        assert_eq!(format_f64(results.beta_0, 2, false), "10.73");
        assert_eq!(format_f64(results.r_squared, 4, false), "0.8288");
    }
}
