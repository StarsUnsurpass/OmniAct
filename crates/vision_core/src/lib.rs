use pyo3::prelude::*;
use pyo3::types::PyBytes;
use image::{GenericImageView, DynamicImage, ImageReader};
use std::io::Cursor;

/// Calculates the difference ratio between two images (0.0 = identical, 1.0 = completely different).
/// Input: Two byte arrays (PNG/JPG).
#[pyfunction]
fn calculate_pixel_diff(img1_data: &[u8], img2_data: &[u8]) -> PyResult<f64> {
    let img1 = load_image(img1_data).map_err(|e| pyo3::exceptions::PyValueError::new_err(e))?;
    let img2 = load_image(img2_data).map_err(|e| pyo3::exceptions::PyValueError::new_err(e))?;

    let (w1, h1) = img1.dimensions();
    let (w2, h2) = img2.dimensions();

    // If dimensions match exactly, compare directly.
    // If not, resize img2 to match img1 for a rough comparison.
    let img2_adjusted = if w1 != w2 || h1 != h2 {
        img2.resize_exact(w1, h1, image::imageops::FilterType::Nearest)
    } else {
        img2
    };

    let diff_ratio = compute_diff(&img1, &img2_adjusted);
    Ok(diff_ratio)
}

fn load_image(data: &[u8]) -> Result<DynamicImage, String> {
    ImageReader::new(Cursor::new(data))
        .with_guessed_format()
        .map_err(|e| e.to_string())?
        .decode()
        .map_err(|e| e.to_string())
}

fn compute_diff(img1: &DynamicImage, img2: &DynamicImage) -> f64 {
    let (width, height) = img1.dimensions();
    let mut diff_pixels = 0;
    let total_pixels = width as u64 * height as u64;

    if total_pixels == 0 {
        return 0.0;
    }

    // Simple pixel-by-pixel comparison
    // We convert to RGB8 for simplicity
    let rgb1 = img1.to_rgb8();
    let rgb2 = img2.to_rgb8();

    for (p1, p2) in rgb1.pixels().zip(rgb2.pixels()) {
        let r_diff = (p1[0] as i16 - p2[0] as i16).abs();
        let g_diff = (p1[1] as i16 - p2[1] as i16).abs();
        let b_diff = (p1[2] as i16 - p2[2] as i16).abs();

        // Threshold for "different": if sum of channel diffs > 30 (arbitrary small tolerance)
        if r_diff + g_diff + b_diff > 30 {
            diff_pixels += 1;
        }
    }

    diff_pixels as f64 / total_pixels as f64
}

/// A Python module implemented in Rust.
#[pymodule]
fn vision_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(calculate_pixel_diff, m)?)?;
    Ok(())
}
