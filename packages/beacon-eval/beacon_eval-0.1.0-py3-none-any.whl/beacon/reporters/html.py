"""HTML report generation for Beacon."""

import html
from pathlib import Path

from beacon.models import BenchmarkResult


def generate_html_report(result: BenchmarkResult, output_path: Path) -> None:
    """Generate an HTML report for benchmark results.

    Args:
        result: The benchmark result to report.
        output_path: Path to write the HTML report.
    """
    html = _generate_html(result)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


def _generate_html(result: BenchmarkResult) -> str:
    """Generate HTML content for the report."""
    # Escape user-provided content to prevent XSS
    config_name = html.escape(result.config.name)
    best_strategy = html.escape(result.best_strategy)
    recommendation = html.escape(result.recommendation)

    # Prepare data for charts
    strategies = [html.escape(sr.strategy.name) for sr in result.strategy_results]
    mrr_scores = [sr.metrics.mrr for sr in result.strategy_results]
    recall_scores = [sr.metrics.recall_at_5 for sr in result.strategy_results]
    ndcg_scores = [sr.metrics.ndcg_at_10 for sr in result.strategy_results]

    # Generate comparison table rows
    table_rows = ""
    for sr in result.strategy_results:
        is_best = sr.strategy.name == result.best_strategy
        row_class = "best-strategy" if is_best else ""
        badge = '<span class="badge">★ Best</span>' if is_best else ""
        strategy_name = html.escape(sr.strategy.name)

        table_rows += f"""
        <tr class="{row_class}">
            <td>{strategy_name} {badge}</td>
            <td>{html.escape(sr.strategy.strategy_type.value)}</td>
            <td>{sr.strategy.chunk_size}</td>
            <td>{sr.strategy.chunk_overlap}</td>
            <td>{sr.metrics.num_chunks}</td>
            <td class="metric">{sr.metrics.mrr:.4f}</td>
            <td class="metric">{sr.metrics.recall_at_1:.4f}</td>
            <td class="metric">{sr.metrics.recall_at_5:.4f}</td>
            <td class="metric">{sr.metrics.recall_at_10:.4f}</td>
            <td class="metric">{sr.metrics.ndcg_at_10:.4f}</td>
            <td>{sr.metrics.avg_latency_ms:.2f}ms</td>
        </tr>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Beacon Benchmark Report - {config_name}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        :root {{
            --primary: #2563eb;
            --success: #16a34a;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --text-secondary: #64748b;
            --border: #e2e8f0;
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding: 2rem;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        header {{
            text-align: center;
            margin-bottom: 2rem;
        }}
        h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}
        .subtitle {{
            color: var(--text-secondary);
        }}
        .card {{
            background: var(--card-bg);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .card h2 {{
            font-size: 1.25rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border);
        }}
        .recommendation {{
            background: linear-gradient(135deg, #ecfdf5, #d1fae5);
            border-left: 4px solid var(--success);
        }}
        .recommendation .best {{
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--success);
            margin-bottom: 0.5rem;
        }}
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        .chart-container {{
            background: var(--card-bg);
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }}
        th, td {{
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        th {{
            background: var(--bg);
            font-weight: 600;
        }}
        .metric {{
            font-family: monospace;
        }}
        .best-strategy {{
            background: #f0fdf4;
        }}
        .badge {{
            background: var(--success);
            color: white;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            margin-left: 0.5rem;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
        }}
        .stat {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--primary);
        }}
        .stat-label {{
            color: var(--text-secondary);
            font-size: 0.875rem;
        }}
        footer {{
            text-align: center;
            color: var(--text-secondary);
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Beacon Benchmark Report</h1>
            <p class="subtitle">{config_name}</p>
        </header>

        <div class="card recommendation">
            <div class="best">★ Best Strategy: {best_strategy}</div>
            <p>{recommendation}</p>
        </div>

        <div class="card">
            <h2>Summary Statistics</h2>
            <div class="stats-grid">
                <div class="stat">
                    <div class="stat-value">{len(result.strategy_results)}</div>
                    <div class="stat-label">Strategies Tested</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{len(result.config.documents)}</div>
                    <div class="stat-label">Documents</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{result.strategy_results[0].metrics.num_queries}</div>
                    <div class="stat-label">Queries</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{result.total_time_ms/1000:.1f}s</div>
                    <div class="stat-label">Total Time</div>
                </div>
            </div>
        </div>

        <div class="charts-grid">
            <div class="chart-container">
                <div id="mrr-chart"></div>
            </div>
            <div class="chart-container">
                <div id="recall-chart"></div>
            </div>
        </div>

        <div class="card">
            <h2>Detailed Results</h2>
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th>Strategy</th>
                            <th>Type</th>
                            <th>Chunk Size</th>
                            <th>Overlap</th>
                            <th>Chunks</th>
                            <th>MRR</th>
                            <th>R@1</th>
                            <th>R@5</th>
                            <th>R@10</th>
                            <th>NDCG@10</th>
                            <th>Latency</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
        </div>

        <footer>
            Generated by <strong>Beacon</strong> - RAG Chunking Strategy Benchmarking Toolkit
        </footer>
    </div>

    <script>
        // MRR Chart
        var mrrData = [{{
            x: {strategies},
            y: {mrr_scores},
            type: 'bar',
            marker: {{
                color: {mrr_scores}.map((v, i) =>
                    '{best_strategy}' === {strategies}[i] ? '#16a34a' : '#2563eb'
                )
            }}
        }}];
        var mrrLayout = {{
            title: 'Mean Reciprocal Rank (MRR)',
            yaxis: {{ range: [0, 1], title: 'Score' }},
            margin: {{ t: 40, b: 60 }}
        }};
        Plotly.newPlot('mrr-chart', mrrData, mrrLayout, {{responsive: true}});

        // Recall Chart
        var recallData = [
            {{
                x: {strategies},
                y: {recall_scores},
                name: 'Recall@5',
                type: 'bar'
            }},
            {{
                x: {strategies},
                y: {ndcg_scores},
                name: 'NDCG@10',
                type: 'bar'
            }}
        ];
        var recallLayout = {{
            title: 'Recall@5 vs NDCG@10',
            yaxis: {{ range: [0, 1], title: 'Score' }},
            margin: {{ t: 40, b: 60 }},
            barmode: 'group'
        }};
        Plotly.newPlot('recall-chart', recallData, recallLayout, {{responsive: true}});
    </script>
</body>
</html>"""
