const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const port = 3000;

function applyFunction(combination) {
    // Example function: Calculate sum of values in combination
    return combination.reduce((sum, value) => sum + value, 0);
}

app.use(bodyParser.json());

app.post('/applyFunction', (req, res) => {
    const combinations = req.body.combinations;

    if (!combinations || !Array.isArray(combinations)) {
        return res.status(400).json({ error: 'Invalid combinations provided' });
    }

    const results = combinations.map(combination => applyFunction(combination));

    res.json({ results });
});

app.listen(port, () => {
    console.log(`Server is listening at http://localhost:${port}`);
});
