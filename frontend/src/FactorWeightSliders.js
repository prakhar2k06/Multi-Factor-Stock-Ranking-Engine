import React, { useState } from "react";
import { Slider, Button, Typography, Box, Grid, Paper } from "@mui/material";

export default function FactorWeightSliders({ onSubmit, disabled = false }) {
    const [weights, setWeights] = useState({
        value: 0.2,
        size: 0.2,
        momentum: 0.2,
        lowvol: 0.15,
        quality: 0.15,
        market_risk: 0.1,
    });

    const handleChange = (factor) => (event, value) => {
        setWeights({ ...weights, [factor]: value });
    };

    // Clean factor name for display
    const pretty = (str) =>
        str
            .replace("_", " ")
            .replace(/\b\w/g, (c) => c.toUpperCase());

    return (
        <Paper elevation={3} sx={{ padding: 4, marginTop: 4 }}>
            <Typography variant="h5" gutterBottom>
                Factor Weight Settings
            </Typography>

            <Typography variant="body2" color="textSecondary" gutterBottom>
                Adjust how much influence each factor has on the stock ranking.
            </Typography>

            <Grid container spacing={3}>
                {Object.keys(weights).map((factor) => (
                    <Grid item xs={12} key={factor}>
                        <Typography sx={{ fontWeight: 500 }}>
                            {pretty(factor)} — {weights[factor]}
                        </Typography>

                        <Slider
                            value={weights[factor]}
                            min={0}
                            max={1}
                            step={0.01}
                            disabled={disabled}
                            onChange={handleChange(factor)}
                        />
                    </Grid>
                ))}
            </Grid>

            <Button
                variant="contained"
                color="primary"
                sx={{ marginTop: 3 }}
                fullWidth
                disabled={disabled}
                onClick={() => onSubmit(weights)}
            >
                Generate Rankings
            </Button>
        </Paper>
    );
}
