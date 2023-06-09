const express = require('express');
const mysql = require('mysql');
const app = express();
const port = 3000;
const db = mysql.createConnection({
  host: 'localhost',
  user: 'noah',
  password: '12345',
  database: 'productdb'
});

db.connect(err => {
  if (err) {
    console.error('Database connection error:', err);
  } else {
    console.log('Connected to the database');
  }
});

app.post('/products', (req, res) => {
  const { name, price, description, quantity } = req.body;
  const query = 'INSERT INTO products (name, price, description, quantity) VALUES (?, ?, ?, ?)';
  const values = [name, price, description, quantity];
  db.query(query, values, (err, result) => {
    if (err) {
      console.error('Error creating product:', err);
      res.status(500).json({ message: 'Error creating product' });
    } else {
      res.status(201).json({ message: 'Product created successfully' });
    }
  });
});


app.get('/products', (req, res) => {
  const query = 'SELECT * FROM products';
  db.query(query, (err, results) => {
    if (err) {
      console.error('Error retrieving products:', err);
      res.status(500).json({ message: 'Error retrieving products' });
    } else {
      res.json(results);
    }
  });
});

app.get('/products/:id', (req, res) => {
  const productId = req.params.id;
  const query = 'SELECT * FROM products WHERE id = ?';
  db.query(query, [productId], (err, result) => {
    if (err) {
      console.error('Error retrieving product:', err);
      res.status(500).json({ message: 'Error retrieving product' });
    } else if (result.length === 0) {
      res.status(404).json({ message: 'Product not found' });
    } else {
      res.json(result[0]);
    }
  });
});

app.put('/products/:id', (req, res) => {
  const productId = req.params.id;
  const { name, price, description, quantity } = req.body;
  const query = 'UPDATE products SET name = ?, price = ?, description = ?, quantity = ? WHERE id = ?';
  const values = [name, price, description, quantity, productId];
  db.query(query, values, (err, result) => {
    if (err) {
      console.error('Error updating product:', err);
      res.status(500).json({ message: 'Error updating product' });
    } else if (result.affectedRows === 0) {
      res.status(404).json({ message: 'Product not found' });
    } else {
      res.json({ message: 'Product updated successfully' });
    }
  });
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
