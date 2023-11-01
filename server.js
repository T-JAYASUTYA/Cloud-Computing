const express = require('express');
const path = require('path');
const app = express();
const port = process.env.PORT || 3000; // Use port 3000 by default, or specify one in the environment variable

// Serve static files (like your styles.css and script.js)
app.use(express.static(path.join(__dirname, 'public')));

// Define a route to serve your landing page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
