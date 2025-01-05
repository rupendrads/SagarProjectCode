const express = require('express');
const bodyParser = require('body-parser');

class Optimizer {
    constructor(paramsJson, calculateCombinations = true) {
        this.params = JSON.parse(paramsJson);
        this.calculateCombinations = calculateCombinations;
    }

    applyRule(combination, rule) {
        if (rule) {
            const parameterList = rule["parameter_list"];
            const relation = rule["relation"];
    
            if (parameterList && relation) {
                const paramValues = {};
                for (const paramName of parameterList) {
                    paramValues[paramName] = combination[paramName];
                }
    
                try {
                    const { long_ma, short_ma } = paramValues; // Destructure long_ma and short_ma from paramValues
                    return eval(relation); // Evaluate the relation expression in the context of paramValues
                } catch (error) {
                    console.error("Error evaluating rule:", error);
                    return false;
                }
            }
        }
        return true; // If no rule specified or if there's an error evaluating the rule, consider it passed
    }
}

const app = express();
const port = 3000;
// app.use(bodyParser.urlencoded({ extended: true }));
// app.use(bodyParser.json());
app.use(bodyParser.json({ limit: '10mb' }));
app.use(bodyParser.urlencoded({ extended: true, limit: '10mb' }));
app.post('/applyRule', (req, res) => {
    // console.log("apply rule invoked")
    const paramsJson = `{
        "rule": {"parameter_list": ["short_ma", "long_ma"], "relation": "5 <= long_ma - short_ma && long_ma - short_ma < 20"},
        "moving_average":{"default_value":"ema", "types" :["sma","ema","dma", "kama"]}
    
    }`;
    const combinations = req.body.combinations;

    if (!paramsJson || !combinations) {
        return res.status(400).json({ error: 'Invalid parameters provided' });
    }

    const optimizer = new Optimizer(paramsJson);
    const rule = optimizer.params["rule"];

    const results = [];
    for (const combination of combinations) {
        const result = optimizer.applyRule(combination, rule);
        if (result){
        results.push({ combination });
        }
    }

    res.json({ results });
});

app.listen(port, () => {
    console.log(`Server is listening at http://localhost:${port}`);
});
