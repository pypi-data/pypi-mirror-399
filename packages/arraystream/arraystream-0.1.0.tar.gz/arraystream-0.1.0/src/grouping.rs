use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use pyo3::exceptions::{PyTypeError, PyValueError};

/// Supported numeric typecodes
const SUPPORTED_TYPECODES: &[u8] = b"bBhHiIlLfd";

fn is_supported_typecode(typecode: u8) -> bool {
    SUPPORTED_TYPECODES.contains(&typecode)
}

fn check_array_type(arr: &PyAny) -> PyResult<()> {
    let array_module = PyModule::import(arr.py(), "array")?;
    let array_type = array_module.getattr("array")?;
    
    if !arr.is_instance(array_type)? {
        return Err(PyTypeError::new_err("Expected array.array"));
    }
    
    let typecode: u8 = arr.getattr("typecode")?.extract()?;
    if !is_supported_typecode(typecode) {
        return Err(PyTypeError::new_err(format!(
            "Unsupported typecode: '{}'",
            typecode as char
        )));
    }
    
    Ok(())
}

/// Run-length encode an array
#[pyfunction]
pub fn run_length_encode(py: Python, arr: &PyAny) -> PyResult<PyObject> {
    check_array_type(arr)?;
    
    let typecode: u8 = arr.getattr("typecode")?.extract()?;
    let len = arr.len()?;
    
    if len == 0 {
        let array_module = PyModule::import(py, "array")?;
        let array_type = array_module.getattr("array")?;
        let typecode_str = (typecode as char).to_string();
        let empty_values: Vec<u8> = Vec::new();
        let empty_counts: Vec<u64> = Vec::new();
        let result = PyDict::new(py);
        result.set_item("values", array_type.call1((typecode_str.clone(), empty_values))?)?;
        result.set_item("counts", array_type.call1(("L", empty_counts))?)?;
        return Ok(result.to_object(py));
    }
    
    // Convert array to list first, then extract
    let list_obj = arr.call_method0("tolist")?;
    let list_seq: &PyList = list_obj.downcast()?;
    
    match typecode {
        b'i' => {
            let data: Vec<i32> = (0..len).map(|i| list_seq.get_item(i)?.extract::<i32>()).collect::<PyResult<Vec<_>>>()?;
            rle_impl_i32(py, &data, "i")
        }
        b'I' => {
            let data: Vec<u32> = (0..len).map(|i| list_seq.get_item(i)?.extract::<u32>()).collect::<PyResult<Vec<_>>>()?;
            rle_impl_u32(py, &data, "I")
        }
        b'l' => {
            let data: Vec<i64> = (0..len).map(|i| list_seq.get_item(i)?.extract::<i64>()).collect::<PyResult<Vec<_>>>()?;
            rle_impl_i64(py, &data, "l")
        }
        b'L' => {
            let data: Vec<u64> = (0..len).map(|i| list_seq.get_item(i)?.extract::<u64>()).collect::<PyResult<Vec<_>>>()?;
            rle_impl_u64(py, &data, "L")
        }
        b'h' => {
            let data: Vec<i16> = (0..len).map(|i| list_seq.get_item(i)?.extract::<i16>()).collect::<PyResult<Vec<_>>>()?;
            rle_impl_i16(py, &data, "h")
        }
        b'H' => {
            let data: Vec<u16> = (0..len).map(|i| list_seq.get_item(i)?.extract::<u16>()).collect::<PyResult<Vec<_>>>()?;
            rle_impl_u16(py, &data, "H")
        }
        b'b' => {
            let data: Vec<i8> = (0..len).map(|i| list_seq.get_item(i)?.extract::<i8>()).collect::<PyResult<Vec<_>>>()?;
            rle_impl_i8(py, &data, "b")
        }
        b'B' => {
            let data: Vec<u8> = (0..len).map(|i| list_seq.get_item(i)?.extract::<u8>()).collect::<PyResult<Vec<_>>>()?;
            rle_impl_u8(py, &data, "B")
        }
        b'f' => {
            let data: Vec<f32> = (0..len).map(|i| list_seq.get_item(i)?.extract::<f32>()).collect::<PyResult<Vec<_>>>()?;
            rle_impl_f32(py, &data, "f")
        }
        b'd' => {
            let data: Vec<f64> = (0..len).map(|i| list_seq.get_item(i)?.extract::<f64>()).collect::<PyResult<Vec<_>>>()?;
            rle_impl_f64(py, &data, "d")
        }
        _ => Err(PyTypeError::new_err("Unsupported typecode")),
    }
}

fn rle_impl_i32(py: Python, data: &[i32], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut values = Vec::new();
    let mut counts = Vec::new();
    
    if !data.is_empty() {
        let mut current = data[0];
        let mut count = 1u64;
        
        for i in 1..data.len() {
            if data[i] == current {
                count += 1;
            } else {
                values.push(current);
                counts.push(count);
                current = data[i];
                count = 1;
            }
        }
        values.push(current);
        counts.push(count);
    }
    
    let result = PyDict::new(py);
    result.set_item("values", array_type.call1((typecode, values))?)?;
    result.set_item("counts", array_type.call1(("L", counts))?)?;
    Ok(result.to_object(py))
}

fn rle_impl_u32(py: Python, data: &[u32], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut values = Vec::new();
    let mut counts = Vec::new();
    
    if !data.is_empty() {
        let mut current = data[0];
        let mut count = 1u64;
        
        for i in 1..data.len() {
            if data[i] == current {
                count += 1;
            } else {
                values.push(current);
                counts.push(count);
                current = data[i];
                count = 1;
            }
        }
        values.push(current);
        counts.push(count);
    }
    
    let result = PyDict::new(py);
    result.set_item("values", array_type.call1((typecode, values))?)?;
    result.set_item("counts", array_type.call1(("L", counts))?)?;
    Ok(result.to_object(py))
}

fn rle_impl_i64(py: Python, data: &[i64], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut values = Vec::new();
    let mut counts = Vec::new();
    
    if !data.is_empty() {
        let mut current = data[0];
        let mut count = 1u64;
        
        for i in 1..data.len() {
            if data[i] == current {
                count += 1;
            } else {
                values.push(current);
                counts.push(count);
                current = data[i];
                count = 1;
            }
        }
        values.push(current);
        counts.push(count);
    }
    
    let result = PyDict::new(py);
    result.set_item("values", array_type.call1((typecode, values))?)?;
    result.set_item("counts", array_type.call1(("L", counts))?)?;
    Ok(result.to_object(py))
}

fn rle_impl_u64(py: Python, data: &[u64], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut values = Vec::new();
    let mut counts = Vec::new();
    
    if !data.is_empty() {
        let mut current = data[0];
        let mut count = 1u64;
        
        for i in 1..data.len() {
            if data[i] == current {
                count += 1;
            } else {
                values.push(current);
                counts.push(count);
                current = data[i];
                count = 1;
            }
        }
        values.push(current);
        counts.push(count);
    }
    
    let result = PyDict::new(py);
    result.set_item("values", array_type.call1((typecode, values))?)?;
    result.set_item("counts", array_type.call1(("L", counts))?)?;
    Ok(result.to_object(py))
}

fn rle_impl_i16(py: Python, data: &[i16], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut values = Vec::new();
    let mut counts = Vec::new();
    
    if !data.is_empty() {
        let mut current = data[0];
        let mut count = 1u64;
        
        for i in 1..data.len() {
            if data[i] == current {
                count += 1;
            } else {
                values.push(current);
                counts.push(count);
                current = data[i];
                count = 1;
            }
        }
        values.push(current);
        counts.push(count);
    }
    
    let result = PyDict::new(py);
    result.set_item("values", array_type.call1((typecode, values))?)?;
    result.set_item("counts", array_type.call1(("L", counts))?)?;
    Ok(result.to_object(py))
}

fn rle_impl_u16(py: Python, data: &[u16], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut values = Vec::new();
    let mut counts = Vec::new();
    
    if !data.is_empty() {
        let mut current = data[0];
        let mut count = 1u64;
        
        for i in 1..data.len() {
            if data[i] == current {
                count += 1;
            } else {
                values.push(current);
                counts.push(count);
                current = data[i];
                count = 1;
            }
        }
        values.push(current);
        counts.push(count);
    }
    
    let result = PyDict::new(py);
    result.set_item("values", array_type.call1((typecode, values))?)?;
    result.set_item("counts", array_type.call1(("L", counts))?)?;
    Ok(result.to_object(py))
}

fn rle_impl_i8(py: Python, data: &[i8], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut values = Vec::new();
    let mut counts = Vec::new();
    
    if !data.is_empty() {
        let mut current = data[0];
        let mut count = 1u64;
        
        for i in 1..data.len() {
            if data[i] == current {
                count += 1;
            } else {
                values.push(current);
                counts.push(count);
                current = data[i];
                count = 1;
            }
        }
        values.push(current);
        counts.push(count);
    }
    
    let result = PyDict::new(py);
    result.set_item("values", array_type.call1((typecode, values))?)?;
    result.set_item("counts", array_type.call1(("L", counts))?)?;
    Ok(result.to_object(py))
}

fn rle_impl_u8(py: Python, data: &[u8], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut values = Vec::new();
    let mut counts = Vec::new();
    
    if !data.is_empty() {
        let mut current = data[0];
        let mut count = 1u64;
        
        for i in 1..data.len() {
            if data[i] == current {
                count += 1;
            } else {
                values.push(current);
                counts.push(count);
                current = data[i];
                count = 1;
            }
        }
        values.push(current);
        counts.push(count);
    }
    
    let result = PyDict::new(py);
    result.set_item("values", array_type.call1((typecode, values))?)?;
    result.set_item("counts", array_type.call1(("L", counts))?)?;
    Ok(result.to_object(py))
}

fn rle_impl_f32(py: Python, data: &[f32], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut values = Vec::new();
    let mut counts = Vec::new();
    
    if !data.is_empty() {
        let mut current = data[0];
        let mut count = 1u64;
        
        for i in 1..data.len() {
            if data[i] == current {
                count += 1;
            } else {
                values.push(current);
                counts.push(count);
                current = data[i];
                count = 1;
            }
        }
        values.push(current);
        counts.push(count);
    }
    
    let result = PyDict::new(py);
    result.set_item("values", array_type.call1((typecode, values))?)?;
    result.set_item("counts", array_type.call1(("L", counts))?)?;
    Ok(result.to_object(py))
}

fn rle_impl_f64(py: Python, data: &[f64], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut values = Vec::new();
    let mut counts = Vec::new();
    
    if !data.is_empty() {
        let mut current = data[0];
        let mut count = 1u64;
        
        for i in 1..data.len() {
            if data[i] == current {
                count += 1;
            } else {
                values.push(current);
                counts.push(count);
                current = data[i];
                count = 1;
            }
        }
        values.push(current);
        counts.push(count);
    }
    
    let result = PyDict::new(py);
    result.set_item("values", array_type.call1((typecode, values))?)?;
    result.set_item("counts", array_type.call1(("L", counts))?)?;
    Ok(result.to_object(py))
}

/// Group consecutive equal elements
#[pyfunction]
pub fn groupby_runs(py: Python, arr: &PyAny) -> PyResult<PyObject> {
    check_array_type(arr)?;
    
    let typecode: u8 = arr.getattr("typecode")?.extract()?;
    let len = arr.len()?;
    
    if len == 0 {
        return Ok(PyList::empty(py).to_object(py));
    }
    
    // Extract array elements by converting to list first
    let list_obj = arr.call_method0("tolist")?;
    let list: &PyList = list_obj.downcast()?;
    
    match typecode {
        b'i' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: i32 = list.get_item(i)?.extract()?;
                data.push(val);
            }
            groupby_runs_impl_i32(py, &data, "i")
        }
        b'I' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: u32 = list.get_item(i)?.extract()?;
                data.push(val);
            }
            groupby_runs_impl_u32(py, &data, "I")
        }
        b'l' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: i64 = list.get_item(i)?.extract()?;
                data.push(val);
            }
            groupby_runs_impl_i64(py, &data, "l")
        }
        b'L' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: u64 = list.get_item(i)?.extract()?;
                data.push(val);
            }
            groupby_runs_impl_u64(py, &data, "L")
        }
        b'h' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: i16 = list.get_item(i)?.extract()?;
                data.push(val);
            }
            groupby_runs_impl_i16(py, &data, "h")
        }
        b'H' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: u16 = list.get_item(i)?.extract()?;
                data.push(val);
            }
            groupby_runs_impl_u16(py, &data, "H")
        }
        b'b' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: i8 = list.get_item(i)?.extract()?;
                data.push(val);
            }
            groupby_runs_impl_i8(py, &data, "b")
        }
        b'B' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: u8 = list.get_item(i)?.extract()?;
                data.push(val);
            }
            groupby_runs_impl_u8(py, &data, "B")
        }
        b'f' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: f32 = list.get_item(i)?.extract()?;
                data.push(val);
            }
            groupby_runs_impl_f32(py, &data, "f")
        }
        b'd' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: f64 = list.get_item(i)?.extract()?;
                data.push(val);
            }
            groupby_runs_impl_f64(py, &data, "d")
        }
        _ => Err(PyTypeError::new_err("Unsupported typecode")),
    }
}

fn groupby_runs_impl_i32(py: Python, data: &[i32], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut groups = Vec::new();
    
    if !data.is_empty() {
        let mut start = 0;
        let mut current = data[0];
        
        for i in 1..data.len() {
            if data[i] != current {
                let group = array_type.call1((typecode, data[start..i].to_vec()))?;
                groups.push(group);
                start = i;
                current = data[i];
            }
        }
        let group = array_type.call1((typecode, data[start..data.len()].to_vec()))?;
        groups.push(group);
    }
    
    let py_list = PyList::new(py, groups);
    Ok(py_list.to_object(py))
}

fn groupby_runs_impl_u32(py: Python, data: &[u32], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut groups = Vec::new();
    
    if !data.is_empty() {
        let mut start = 0;
        let mut current = data[0];
        
        for i in 1..data.len() {
            if data[i] != current {
                let group = array_type.call1((typecode, data[start..i].to_vec()))?;
                groups.push(group);
                start = i;
                current = data[i];
            }
        }
        let group = array_type.call1((typecode, data[start..data.len()].to_vec()))?;
        groups.push(group);
    }
    
    let py_list = PyList::new(py, groups);
    Ok(py_list.to_object(py))
}

fn groupby_runs_impl_i64(py: Python, data: &[i64], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut groups = Vec::new();
    
    if !data.is_empty() {
        let mut start = 0;
        let mut current = data[0];
        
        for i in 1..data.len() {
            if data[i] != current {
                let group = array_type.call1((typecode, data[start..i].to_vec()))?;
                groups.push(group);
                start = i;
                current = data[i];
            }
        }
        let group = array_type.call1((typecode, data[start..data.len()].to_vec()))?;
        groups.push(group);
    }
    
    let py_list = PyList::new(py, groups);
    Ok(py_list.to_object(py))
}

fn groupby_runs_impl_u64(py: Python, data: &[u64], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut groups = Vec::new();
    
    if !data.is_empty() {
        let mut start = 0;
        let mut current = data[0];
        
        for i in 1..data.len() {
            if data[i] != current {
                let group = array_type.call1((typecode, data[start..i].to_vec()))?;
                groups.push(group);
                start = i;
                current = data[i];
            }
        }
        let group = array_type.call1((typecode, data[start..data.len()].to_vec()))?;
        groups.push(group);
    }
    
    let py_list = PyList::new(py, groups);
    Ok(py_list.to_object(py))
}

fn groupby_runs_impl_i16(py: Python, data: &[i16], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut groups = Vec::new();
    
    if !data.is_empty() {
        let mut start = 0;
        let mut current = data[0];
        
        for i in 1..data.len() {
            if data[i] != current {
                let group = array_type.call1((typecode, data[start..i].to_vec()))?;
                groups.push(group);
                start = i;
                current = data[i];
            }
        }
        let group = array_type.call1((typecode, data[start..data.len()].to_vec()))?;
        groups.push(group);
    }
    
    let py_list = PyList::new(py, groups);
    Ok(py_list.to_object(py))
}

fn groupby_runs_impl_u16(py: Python, data: &[u16], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut groups = Vec::new();
    
    if !data.is_empty() {
        let mut start = 0;
        let mut current = data[0];
        
        for i in 1..data.len() {
            if data[i] != current {
                let group = array_type.call1((typecode, data[start..i].to_vec()))?;
                groups.push(group);
                start = i;
                current = data[i];
            }
        }
        let group = array_type.call1((typecode, data[start..data.len()].to_vec()))?;
        groups.push(group);
    }
    
    let py_list = PyList::new(py, groups);
    Ok(py_list.to_object(py))
}

fn groupby_runs_impl_i8(py: Python, data: &[i8], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut groups = Vec::new();
    
    if !data.is_empty() {
        let mut start = 0;
        let mut current = data[0];
        
        for i in 1..data.len() {
            if data[i] != current {
                let group = array_type.call1((typecode, data[start..i].to_vec()))?;
                groups.push(group);
                start = i;
                current = data[i];
            }
        }
        let group = array_type.call1((typecode, data[start..data.len()].to_vec()))?;
        groups.push(group);
    }
    
    let py_list = PyList::new(py, groups);
    Ok(py_list.to_object(py))
}

fn groupby_runs_impl_u8(py: Python, data: &[u8], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut groups = Vec::new();
    
    if !data.is_empty() {
        let mut start = 0;
        let mut current = data[0];
        
        for i in 1..data.len() {
            if data[i] != current {
                let group = array_type.call1((typecode, data[start..i].to_vec()))?;
                groups.push(group);
                start = i;
                current = data[i];
            }
        }
        let group = array_type.call1((typecode, data[start..data.len()].to_vec()))?;
        groups.push(group);
    }
    
    let py_list = PyList::new(py, groups);
    Ok(py_list.to_object(py))
}

fn groupby_runs_impl_f32(py: Python, data: &[f32], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut groups = Vec::new();
    
    if !data.is_empty() {
        let mut start = 0;
        let mut current = data[0];
        
        for i in 1..data.len() {
            if data[i] != current {
                let group = array_type.call1((typecode, data[start..i].to_vec()))?;
                groups.push(group);
                start = i;
                current = data[i];
            }
        }
        let group = array_type.call1((typecode, data[start..data.len()].to_vec()))?;
        groups.push(group);
    }
    
    let py_list = PyList::new(py, groups);
    Ok(py_list.to_object(py))
}

fn groupby_runs_impl_f64(py: Python, data: &[f64], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut groups = Vec::new();
    
    if !data.is_empty() {
        let mut start = 0;
        let mut current = data[0];
        
        for i in 1..data.len() {
            if data[i] != current {
                let group = array_type.call1((typecode, data[start..i].to_vec()))?;
                groups.push(group);
                start = i;
                current = data[i];
            }
        }
        let group = array_type.call1((typecode, data[start..data.len()].to_vec()))?;
        groups.push(group);
    }
    
    let py_list = PyList::new(py, groups);
    Ok(py_list.to_object(py))
}
