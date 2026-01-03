use pyo3::prelude::*;

/* ---------------- Core functions ---------------- */

#[pyfunction]
fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[pyfunction]
fn multiply(a: i32, b: i32) -> i32 {
    a * b
}

#[pyfunction]
fn power(base: f64, exponent: f64) -> f64 {
    base.powf(exponent)
}

#[pyfunction]
fn sine(angle: f64) -> f64 {
    angle.sin()
}

#[pyfunction]
fn cosine(angle: f64) -> f64 {
    angle.cos()
}

fn register_algebra(m: &Bound<'_, PyModule>) -> PyResult<()> {
    let sub = PyModule::new(m.py(), "algebra")?;
    sub.add_function(wrap_pyfunction!(add, &sub)?)?;
    sub.add_function(wrap_pyfunction!(multiply, &sub)?)?;
    sub.add_function(wrap_pyfunction!(power, &sub)?)?;
    m.add_submodule(&sub)?;
    Ok(())
}

fn register_trigonometry(m: &Bound<'_, PyModule>) -> PyResult<()> {
    let sub = PyModule::new(m.py(), "trigonometry")?;
    sub.add_function(wrap_pyfunction!(sine, &sub)?)?;
    sub.add_function(wrap_pyfunction!(cosine, &sub)?)?;
    m.add_submodule(&sub)?;
    Ok(())
}

#[pymodule]
fn fastmath(m: &Bound<'_, PyModule>) -> PyResult<()> {
    register_algebra(m)?;
    register_trigonometry(m)?;
    Ok(())
}

/* ---------------- Tests ---------------- */

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(2, 2), 4);
    }

    #[test]
    fn test_multiply() {
        assert_eq!(multiply(3, 3), 9);
    }

    #[test]
    fn test_power() {
        assert_eq!(power(2.0, 3.0), 8.0);
    }

    #[test]
    fn test_sine() {
        assert!((sine(std::f64::consts::PI / 2.0) - 1.0).abs() < 1e-10);
    }

    #[test]
    fn test_cosine() {
        assert!((cosine(0.0) - 1.0).abs() < 1e-10);
    }
}
