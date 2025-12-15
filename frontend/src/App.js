import React, { useState } from "react";
import { Container, Typography, Box, CircularProgress } from "@mui/material";
import FactorWeightSliders from "./FactorWeightSliders";

export default function App() {
    const [rankings, setRankings] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleGenerate = async (weights) => {
        setLoading(true);
        setRankings([]); 

        try {
            const res = await fetch("http://127.0.0.1:8000/rank", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(weights),
            });

            const data = await res.json();
            const ranked = data.ranked_stocks?.slice(0, 20) || [];
            setRankings(ranked);
        } catch (error) {
            console.error("Ranking request failed:", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container maxWidth="md" sx={{ paddingTop: 4 }}>
            {/* MAIN TITLE */}
            <Typography variant="h4" align="center" gutterBottom>
                📈 Multi Factor Stock Ranking Engine
            </Typography>

            <Typography variant="subtitle1" align="center" gutterBottom>
                Adjust factor weights and generate the top-ranked U.S. equities
            </Typography>

            {/* SLIDERS */}
            <FactorWeightSliders onSubmit={handleGenerate} disabled={loading} />

            {/* LOADING SPINNER */}
            {loading && (
                <Box sx={{ display: "flex", justifyContent: "center", marginTop: 4 }}>
                    <CircularProgress size={48} />
                </Box>
            )}

            {/* RANKING TABLE */}
            {!loading && rankings.length > 0 && (
                <Box sx={{ marginTop: 6 }}>
                    <Typography variant="h5" gutterBottom>
                        Top 20 Ranked Stocks
                    </Typography>

                    <table style={{ width: "100%", borderCollapse: "collapse" }}>
                        <thead>
                            <tr style={{ background: "#f0f0f0" }}>
                                <th style={{ padding: "10px", border: "1px solid #ddd" }}>Rank</th>
                                <th style={{ padding: "10px", border: "1px solid #ddd" }}>Ticker</th>
                                <th style={{ padding: "10px", border: "1px solid #ddd" }}>Score</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rankings.map(([ticker, score], index) => (
                                <tr key={index}>
                                    <td style={{ padding: "10px", border: "1px solid #ddd" }}>{index + 1}</td>
                                    <td style={{ padding: "10px", border: "1px solid #ddd" }}>{ticker}</td>
                                    <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                                        {score.toFixed(4)}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </Box>
            )}
        </Container>
    );
}

