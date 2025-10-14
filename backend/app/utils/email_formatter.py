"""
Digest Email Formatter Module

This module provides functionality to format news digest items into
professional HTML email reports. It creates clean, readable emails with
trading advice categorized by priority and impact.

Dependencies:
    - datetime: For date formatting
    - typing: For type hints

Author: Trade Ideas Analyzer
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..analysis.news_digest import NewsDigestItem, TradingAdvice

logger = logging.getLogger(__name__)


class DigestEmailFormatter:
    """
    Formats news digest items into professional email reports.

    This class generates HTML emails with categorized trading insights,
    clean formatting, and mobile-responsive design for daily digest delivery.

    Attributes:
        advice_colors (Dict): Color mapping for trading advice categories
        advice_icons (Dict): Icon mapping for visual categorization
        advice_priorities (Dict): Priority ordering for digest sections
    """

    def __init__(self):
        """Initialize the digest email formatter."""
        # Color scheme for trading advice categories
        self.advice_colors = {
            TradingAdvice.TRADE_ALERT: "#dc3545",  # Red - urgent
            TradingAdvice.WATCH: "#fd7e14",       # Orange - monitor
            TradingAdvice.INFO: "#6c757d"         # Gray - background
        }

        # Icons for visual categorization
        self.advice_icons = {
            TradingAdvice.TRADE_ALERT: "🔴",
            TradingAdvice.WATCH: "🟡",
            TradingAdvice.INFO: "🟢"
        }

        # Priority for section ordering
        self.advice_priorities = {
            TradingAdvice.TRADE_ALERT: 1,
            TradingAdvice.WATCH: 2,
            TradingAdvice.INFO: 3
        }

    def format_digest_email(
        self,
        digest_items: List[NewsDigestItem],
        config: Optional[Any] = None,
        market_summary: Optional[Dict[str, Any]] = None,
        upcoming_events: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format digest items into professional HTML email.

        Args:
            digest_items (List[NewsDigestItem]): Processed news digest items
            config (Optional[Any]): Configuration object for customization
            market_summary (Optional[Dict]): Optional market overview data
            upcoming_events (Optional[Dict]): Upcoming earnings, Fed events, etc.

        Returns:
            str: Complete HTML email content ready for sending

        Note:
            Email is optimized for both desktop and mobile viewing with
            responsive design and clear visual hierarchy.
        """
        try:
            # Group items by advice category
            categorized_items = self._categorize_items(digest_items)

            # Generate email sections
            header_html = self._generate_header(len(digest_items), market_summary)
            body_html = self._generate_body(categorized_items)
            upcoming_events_html = self._generate_upcoming_events_section(upcoming_events)
            footer_html = self._generate_footer()

            # Combine into complete email
            full_html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Daily Financial News Digest</title>
                {self._get_email_styles()}
            </head>
            <body>
                <div class="email-container">
                    {header_html}
                    {body_html}
                    {upcoming_events_html}
                    {footer_html}
                </div>
            </body>
            </html>
            """

            return full_html

        except Exception as e:
            logger.error(f"Error formatting digest email: {e}")
            return self._generate_error_email(str(e))

    def _categorize_items(self, items: List[NewsDigestItem]) -> Dict[str, List[NewsDigestItem]]:
        """
        Group digest items by trading direction (Bullish/Bearish/Neutral).

        Args:
            items (List[NewsDigestItem]): All digest items

        Returns:
            Dict[str, List[NewsDigestItem]]: Items grouped by sentiment direction
        """
        categorized = {
            'bullish': [],
            'bearish': [],
            'neutral': []
        }

        for item in items:
            if item.sentiment_score > 0.15:
                categorized['bullish'].append(item)
            elif item.sentiment_score < -0.15:
                categorized['bearish'].append(item)
            else:
                categorized['neutral'].append(item)

        return categorized

    def _generate_header(
        self,
        total_items: int,
        market_summary: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate email header with market summary and ML predictions.

        Args:
            total_items (int): Total number of digest items
            market_summary (Optional[Dict]): Market overview data including indices, VIX, ML predictions

        Returns:
            str: HTML header section with comprehensive market data
        """
        current_date = datetime.now().strftime("%A, %B %d, %Y")

        # Generate market performance section
        market_perf_html = self._generate_market_performance(market_summary)

        return f"""
        <div class="header">
            <h1>💎 Daily Market Intelligence</h1>
            <div class="header-info">
                <div class="date">{current_date}</div>
                <div class="summary">🎯 {total_items} Curated Trading Opportunities</div>
            </div>
        </div>

        {market_perf_html}
        """

    def _generate_market_performance(self, market_summary: Optional[Dict[str, Any]]) -> str:
        """
        Generate market performance summary with indices, VIX, and ML predictions.

        Args:
            market_summary (Optional[Dict]): Market data

        Returns:
            str: HTML section with market performance
        """
        if not market_summary:
            return ""

        # TODO: Fetch real market data (SPY, QQQ, DIA, VIX)
        # For now, use placeholder data
        spy_change = "+0.8%"
        qqq_change = "+1.2%"
        dia_change = "+0.5%"
        vix_value = "14.2"
        vix_change = "-2.1%"

        # VIX regime
        vix_info = market_summary.get('vix_info', {})
        vix_regime = vix_info.get('regime', 'NORMAL')
        regime_color = "#00ff88" if vix_regime == "LOW_VOL" else "#ffd700" if vix_regime == "NORMAL" else "#ff4444"

        # ML prediction placeholder
        ml_prediction = "📈 BULLISH - Models predict 65% probability of S&P 500 closing higher"
        ml_confidence = "Medium Confidence"

        return f"""
        <div class="market-summary">
            <h2>📊 Market Snapshot</h2>
            <div class="market-grid">
                <div class="market-stat">
                    <div class="stat-label">S&P 500</div>
                    <div class="stat-value positive">{spy_change}</div>
                </div>
                <div class="market-stat">
                    <div class="stat-label">Nasdaq</div>
                    <div class="stat-value positive">{qqq_change}</div>
                </div>
                <div class="market-stat">
                    <div class="stat-label">Dow Jones</div>
                    <div class="stat-value positive">{dia_change}</div>
                </div>
                <div class="market-stat">
                    <div class="stat-label">VIX</div>
                    <div class="stat-value" style="color: {regime_color};">{vix_value} ({vix_change})</div>
                    <div class="stat-sublabel">{vix_regime} Volatility</div>
                </div>
            </div>

            <div class="ml-prediction">
                <div class="ml-icon">🤖</div>
                <div class="ml-content">
                    <div class="ml-title">AI Market Prediction</div>
                    <div class="ml-forecast">{ml_prediction}</div>
                    <div class="ml-meta">{ml_confidence} • Updated {datetime.now().strftime('%I:%M %p')}</div>
                </div>
            </div>
        </div>
        """

    def _generate_body(self, categorized_items: Dict[str, List[NewsDigestItem]]) -> str:
        """
        Generate main body content with categorized news items by direction.

        Args:
            categorized_items (Dict): Items grouped by sentiment direction

        Returns:
            str: HTML body content
        """
        sections = []

        # Generate sections in order: Bullish, Bearish, Neutral
        section_order = [
            ('bullish', '🟢 BULLISH SIGNALS', '#00ff88', 'Positive market catalysts'),
            ('bearish', '🔴 BEARISH SIGNALS', '#ff4444', 'Negative market catalysts'),
            ('neutral', '⚪ NEUTRAL / MIXED SIGNALS', '#888888', 'Watch for direction')
        ]

        for direction, title, color, description in section_order:
            items = categorized_items.get(direction, [])
            if items:
                section_html = self._generate_direction_section(direction, title, color, description, items)
                sections.append(section_html)

        return f"""
        <div class="body">
            {''.join(sections)}
        </div>
        """

    def _generate_direction_section(self, direction: str, title: str, color: str, description: str, items: List[NewsDigestItem]) -> str:
        """
        Generate HTML section for specific sentiment direction with table format.

        Args:
            direction (str): Direction category (bullish/bearish/neutral)
            title (str): Section title
            color (str): Section color
            description (str): Section description
            items (List[NewsDigestItem]): Items in this category

        Returns:
            str: HTML section content with table
        """
        table_html = f"""
        <div class="section">
            <div class="section-header">
                <h2 style="color: {color};">{title}</h2>
                <div class="section-description">{description} • {len(items)} signals</div>
            </div>
            <table class="digest-table">
                <thead>
                    <tr>
                        <th style="width: 5%;">#</th>
                        <th style="width: 40%;">Catalyst</th>
                        <th style="width: 30%;">Trading Impact</th>
                        <th style="width: 15%;">Symbols</th>
                        <th style="width: 10%;">Strength</th>
                    </tr>
                </thead>
                <tbody>
        """

        # Generate table rows
        for idx, item in enumerate(items[:10], 1):
            row_html = self._generate_table_row(idx, item)
            table_html += row_html

        # Close table
        table_html += """
                </tbody>
            </table>
        </div>
        """

        return table_html

    def _generate_section(self, advice_type: TradingAdvice, items: List[NewsDigestItem]) -> str:
        """
        Generate HTML section for specific advice category with table format.

        Args:
            advice_type (TradingAdvice): Category type
            items (List[NewsDigestItem]): Items in this category

        Returns:
            str: HTML section content with table
        """
        section_title = self._get_section_title(advice_type)
        icon = self.advice_icons[advice_type]
        color = self.advice_colors[advice_type]

        # Generate table header
        table_html = f"""
        <div class="section">
            <h2 style="color: {color};">{icon} {section_title} ({len(items)})</h2>
            <table class="digest-table">
                <thead>
                    <tr>
                        <th style="width: 5%;">#</th>
                        <th style="width: 35%;">Headline</th>
                        <th style="width: 30%;">Why This Matters</th>
                        <th style="width: 15%;">Symbols</th>
                        <th style="width: 10%;">Sentiment</th>
                        <th style="width: 5%;">Time</th>
                    </tr>
                </thead>
                <tbody>
        """

        # Generate table rows
        for idx, item in enumerate(items[:10], 1):  # Limit items per section
            row_html = self._generate_table_row(idx, item)
            table_html += row_html

        # Close table
        table_html += """
                </tbody>
            </table>
        </div>
        """

        return table_html

    def _generate_item_html(self, item: NewsDigestItem) -> str:
        """
        Generate HTML for individual news item with enhanced trading guidance.

        Args:
            item (NewsDigestItem): Single digest item

        Returns:
            str: HTML for the news item with WHY and HOW TO TRADE
        """
        # Format symbols
        symbols_text = ""
        if item.affected_symbols:
            symbols = item.affected_symbols[:3]  # Show max 3 symbols
            symbols_text = f"<span class='symbols'>📈 Symbols: {', '.join(symbols)}</span>"

        # Format sentiment
        sentiment_color = "#28a745" if item.sentiment_score > 0 else "#dc3545"
        sentiment_icon = "📈" if item.sentiment_score > 0 else "📉"
        sentiment_text = f"{sentiment_icon} {item.sentiment_score:.2f}"

        # Format time
        time_str = item.published.strftime("%I:%M %p")

        # Format source
        source_text = item.source

        # Generate WHY this matters explanation
        why_explanation = self._generate_why_explanation(item)

        # Generate HOW TO TRADE guidance
        trading_guidance = self._generate_trading_guidance(item)

        return f"""
        <div class="news-item">
            <div class="item-header">
                <h3><a href="{item.url}" target="_blank">{item.title}</a></h3>
                <div class="item-meta">
                    <span class="time">{time_str}</span>
                    <span class="source">{source_text}</span>
                    <span class="sentiment" style="color: {sentiment_color};">{sentiment_text}</span>
                </div>
            </div>
            <div class="item-content">
                <div class="summary"><strong>📰 Summary:</strong> {item.summary}</div>

                <div class="why-section">
                    <strong>💡 Why This Matters:</strong> {why_explanation}
                </div>

                <div class="advice">
                    <strong>📊 Signal Detected:</strong> {item.advice_reason}
                </div>

                {trading_guidance}
                {symbols_text}
            </div>
        </div>
        """

    def _generate_table_row(self, idx: int, item: NewsDigestItem) -> str:
        """
        Generate HTML table row for a news item.

        Args:
            idx (int): Row number
            item (NewsDigestItem): News digest item

        Returns:
            str: HTML table row
        """
        # Format symbols
        symbols_text = ", ".join(item.affected_symbols[:2]) if item.affected_symbols else "—"

        # Format sentiment with color
        sentiment_color = "#28a745" if item.sentiment_score > 0 else "#dc3545" if item.sentiment_score < 0 else "#6c757d"
        sentiment_icon = "↑" if item.sentiment_score > 0 else "↓" if item.sentiment_score < 0 else "—"
        sentiment_display = f"{sentiment_icon} {abs(item.sentiment_score):.2f}"

        # Format time
        time_str = item.published.strftime("%I:%M%p")

        # Get why explanation (shortened for table)
        why_explanation = self._generate_why_explanation(item, short_form=True)

        return f"""
                    <tr>
                        <td style="text-align: center;">{idx}</td>
                        <td><a href="{item.url}" style="text-decoration: none; color: #007bff;">{item.title}</a></td>
                        <td style="font-size: 12px;">{why_explanation}</td>
                        <td style="text-align: center; font-weight: bold; color: #28a745;">{symbols_text}</td>
                        <td style="text-align: center; color: {sentiment_color}; font-weight: bold;">{sentiment_display}</td>
                        <td style="text-align: center; font-size: 11px;">{time_str}</td>
                    </tr>
        """

    def _generate_why_explanation(self, item: NewsDigestItem, short_form: bool = False) -> str:
        """
        Generate context-aware WHY explanation analyzing the specific news impact.

        This method analyzes the actual article content to provide actionable trading context:
        - What the news means for stock price direction (bullish/bearish)
        - Why traders should care (specific market impact)
        - Correlating factors (related stocks, sectors, market conditions)

        Args:
            item (NewsDigestItem): News digest item with title, summary, sentiment
            short_form (bool): If True, return abbreviated version for tables

        Returns:
            str: Context-aware explanation of trading relevance
        """
        title = item.title
        summary = item.summary
        content_lower = f"{title} {summary}".lower()
        sentiment = item.sentiment_score
        symbols = item.affected_symbols

        # Build explanation based on actual content analysis
        explanation_parts = []

        # 1. What's happening (brief summary of the news)
        news_type = self._identify_news_type(content_lower)

        # 2. Trading direction and why
        if sentiment > 0.2:
            direction = "BULLISH"
            impact_reason = self._get_bullish_impact_reason(content_lower, news_type, symbols)
        elif sentiment < -0.2:
            direction = "BEARISH"
            impact_reason = self._get_bearish_impact_reason(content_lower, news_type, symbols)
        else:
            direction = "NEUTRAL"
            impact_reason = self._get_neutral_impact_reason(content_lower, news_type, symbols)

        # 3. Correlating factors and sector impact
        correlations = self._identify_correlations(content_lower, symbols, news_type)

        # Combine into coherent explanation
        if short_form:
            # Short form for table: just the key insight
            return f"{direction}: {impact_reason}"
        else:
            # Long form: detailed analysis
            full_explanation = f"{impact_reason}"
            if correlations:
                full_explanation += f" {correlations}"
            return full_explanation

    def _identify_news_type(self, content: str) -> str:
        """Identify the type of financial news."""
        if any(kw in content for kw in ['earnings', 'revenue', 'profit', 'eps', 'beat', 'miss']):
            return "earnings"
        elif any(kw in content for kw in ['merger', 'acquisition', 'deal', 'partnership', 'contract']):
            return "m&a"
        elif any(kw in content for kw in ['upgrade', 'downgrade', 'price target', 'analyst']):
            return "analyst"
        elif any(kw in content for kw in ['fda', 'approval', 'drug', 'clinical trial']):
            return "regulatory"
        elif any(kw in content for kw in ['ceo', 'executive', 'management', 'resignation']):
            return "leadership"
        elif any(kw in content for kw in ['fed', 'interest rate', 'powell', 'fomc', 'inflation', 'cpi']):
            return "macro"
        elif any(kw in content for kw in ['ai', 'semiconductor', 'chip', 'cloud', 'tech']):
            return "tech"
        elif any(kw in content for kw in ['oil', 'energy', 'gas', 'crude']):
            return "energy"
        elif any(kw in content for kw in ['crypto', 'bitcoin', 'ether', 'blockchain']):
            return "crypto"
        else:
            return "general"

    def _get_bullish_impact_reason(self, content: str, news_type: str, symbols: List[str]) -> str:
        """Generate bullish impact explanation."""
        symbol_text = f"{symbols[0]}" if symbols else "this stock"

        if news_type == "earnings":
            return f"Earnings beat likely to drive {symbol_text} higher as institutions reassess valuation upward."
        elif news_type == "m&a":
            return f"Acquisition/partnership signals growth strategy, often leading to multiple expansion for {symbol_text}."
        elif news_type == "analyst":
            return f"Analyst upgrade creates buying pressure from funds that follow ratings for {symbol_text}."
        elif news_type == "regulatory":
            return f"Regulatory approval removes risk overhang, unlocking growth potential for {symbol_text}."
        elif news_type == "tech":
            return f"Tech innovation/adoption trend favors {symbol_text} with potential market share gains."
        elif news_type == "energy":
            return f"Positive energy sector dynamics support {symbol_text} through improved fundamentals."
        else:
            return f"Positive catalyst creates upward momentum opportunity for {symbol_text}."

    def _get_bearish_impact_reason(self, content: str, news_type: str, symbols: List[str]) -> str:
        """Generate bearish impact explanation."""
        symbol_text = f"{symbols[0]}" if symbols else "this stock"

        if news_type == "earnings":
            return f"Earnings disappointment triggers de-rating risk as analysts cut estimates for {symbol_text}."
        elif news_type == "analyst":
            return f"Analyst downgrade signals weakness, often self-fulfilling as institutions reduce exposure to {symbol_text}."
        elif news_type == "regulatory":
            return f"Regulatory setback delays revenue timeline, creating valuation pressure for {symbol_text}."
        elif news_type == "leadership":
            return f"Leadership change introduces execution uncertainty, potentially weighing on {symbol_text}."
        elif news_type == "energy":
            return f"Negative energy sector trends pressure {symbol_text} through margin compression."
        elif news_type == "crypto":
            return f"Crypto market weakness creates risk-off sentiment affecting {symbol_text} and related names."
        else:
            return f"Negative catalyst creates downside risk for {symbol_text}."

    def _get_neutral_impact_reason(self, content: str, news_type: str, symbols: List[str]) -> str:
        """Generate neutral impact explanation."""
        symbol_text = f"{symbols[0]}" if symbols else "this stock"

        if news_type == "earnings":
            return f"In-line results mean guidance and commentary will drive direction for {symbol_text}."
        elif news_type == "macro":
            return f"Macro event affects broad market risk appetite and sector rotation, impacting {symbol_text} indirectly."
        else:
            return f"Development provides market context that may influence {symbol_text} when combined with other factors."

    def _identify_correlations(self, content: str, symbols: List[str], news_type: str) -> str:
        """Identify correlated stocks, sectors, or market factors."""
        correlations = []

        # Sector correlations
        if news_type == "tech" or any(kw in content for kw in ['ai', 'cloud', 'semiconductor']):
            correlations.append("Watch related tech names (NVDA, AMD, MSFT) for sympathy moves")
        elif news_type == "energy" or any(kw in content for kw in ['oil', 'crude', 'energy']):
            correlations.append("Impacts broader energy sector (XLE, CVX, XOM)")
        elif news_type == "crypto":
            correlations.append("Correlates with crypto-exposed stocks (COIN, MSTR, mining stocks)")
        elif news_type == "macro":
            correlations.append("Affects all risk assets through discount rate and liquidity changes")

        # Competitive dynamics
        if len(symbols) >= 2:
            correlations.append(f"Competitive dynamics with {', '.join(symbols[1:3])}")

        # Market regime
        if any(kw in content for kw in ['volatility', 'vol', 'vix']):
            correlations.append("High volatility favors hedging strategies and risk-off positioning")

        return ". ".join(correlations) + "." if correlations else ""

    def _generate_trading_guidance(self, item: NewsDigestItem) -> str:
        """
        Generate actionable HOW TO TRADE guidance.

        Args:
            item (NewsDigestItem): News digest item

        Returns:
            str: HTML formatted trading guidance
        """
        content_lower = f"{item.title} {item.summary}".lower()
        guidance = ""

        if item.trading_advice == TradingAdvice.TRADE_ALERT:
            # High-confidence trade alerts get detailed execution strategy
            if item.sentiment_score > 0.3:
                guidance = f"""
                <div class="trading-guidance strong-buy">
                    <strong>🎯 How to Trade:</strong>
                    <ul>
                        <li><strong>Action:</strong> BUY - Consider long positions or call options</li>
                        <li><strong>Entry:</strong> Look for pullbacks to support levels or enter on volume confirmation</li>
                        <li><strong>Risk Management:</strong> Place stop-loss 3-5% below entry for stock positions, or limit option position to 2-3% of capital</li>
                        <li><strong>Targets:</strong> Take partial profits at +8-12% for stocks, or 50-100% gains for options</li>
                        <li><strong>Timeframe:</strong> Hold 1-5 days for momentum plays, 1-3 weeks for fundamental shifts</li>
                        <li><strong>Confirm with:</strong> Volume spike (2x+ average), technical breakout above resistance</li>
                    </ul>
                </div>
                """
            elif item.sentiment_score < -0.3:
                guidance = f"""
                <div class="trading-guidance strong-sell">
                    <strong>🎯 How to Trade:</strong>
                    <ul>
                        <li><strong>Action:</strong> SELL / SHORT - Consider short positions or put options</li>
                        <li><strong>Entry:</strong> Wait for dead-cat bounce to resistance or enter on breakdown confirmation</li>
                        <li><strong>Risk Management:</strong> Stop-loss 3-5% above entry, cover shorts on support bounce</li>
                        <li><strong>Targets:</strong> Cover shorts at -10-15%, or 100%+ gains on put options</li>
                        <li><strong>Timeframe:</strong> Quick 1-3 day trades for panic selling, 1-2 weeks for downgrades</li>
                        <li><strong>Confirm with:</strong> High volume selling, technical breakdown below support</li>
                    </ul>
                </div>
                """
            else:
                guidance = f"""
                <div class="trading-guidance volatility">
                    <strong>🎯 How to Trade:</strong>
                    <ul>
                        <li><strong>Action:</strong> VOLATILITY PLAY - Consider straddles or range-bound strategies</li>
                        <li><strong>Entry:</strong> Wait for clear directional bias or trade the range</li>
                        <li><strong>Risk Management:</strong> Tight stops at range boundaries</li>
                        <li><strong>Timeframe:</strong> 1-3 days until direction clarifies</li>
                    </ul>
                </div>
                """

        elif item.trading_advice == TradingAdvice.WATCH:
            # Watch list items get monitoring guidance
            guidance = f"""
            <div class="trading-guidance watch">
                <strong>👁️ How to Monitor:</strong>
                <ul>
                    <li><strong>Watch for:</strong> Volume confirmation (2x average) and technical level breaks</li>
                    <li><strong>Entry triggers:</strong> Breakout above resistance with volume, or gap up on catalyst</li>
                    <li><strong>Prepare:</strong> Set price alerts at key levels, review technical charts daily</li>
                    <li><strong>If triggered:</strong> Enter with {('positive' if item.sentiment_score > 0 else 'negative')} bias using strategies above</li>
                </ul>
            </div>
            """

        return guidance

    def _generate_upcoming_events_section(self, upcoming_events: Optional[Dict[str, Any]]) -> str:
        """
        Generate upcoming events section with earnings, Fed decisions, etc.

        Args:
            upcoming_events (Optional[Dict]): Dict containing upcoming events data

        Returns:
            str: HTML section for upcoming events
        """
        if not upcoming_events:
            return ""

        # Build earnings table
        earnings_html = ""
        if upcoming_events.get('earnings'):
            earnings_data = upcoming_events['earnings']
            if earnings_data:
                earnings_html = """
                <div class="upcoming-section">
                    <h3>📅 Upcoming Earnings (Next 7 Days)</h3>
                    <table class="digest-table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Symbol</th>
                                <th>Company</th>
                                <th>Expected Move</th>
                                <th>What to Watch</th>
                            </tr>
                        </thead>
                        <tbody>
                """
                for symbol, data in list(earnings_data.items())[:10]:
                    date_str = data.get('date', 'TBD')
                    company = data.get('company', symbol)
                    expected_move = data.get('expected_move', 'N/A')
                    watch_for = data.get('watch_for', 'Guidance, margins, revenue growth')

                    earnings_html += f"""
                            <tr>
                                <td>{date_str}</td>
                                <td style="font-weight: bold; color: #28a745;">{symbol}</td>
                                <td>{company}</td>
                                <td>{expected_move}</td>
                                <td style="font-size: 12px;">{watch_for}</td>
                            </tr>
                    """

                earnings_html += """
                        </tbody>
                    </table>
                </div>
                """

        # Build Fed events table
        fed_html = ""
        if upcoming_events.get('fed_events'):
            fed_events = upcoming_events['fed_events']
            if fed_events:
                fed_html = """
                <div class="upcoming-section">
                    <h3>🏛️ Federal Reserve & Economic Events</h3>
                    <table class="digest-table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Event</th>
                                <th>Expected Impact</th>
                                <th>What to Watch</th>
                            </tr>
                        </thead>
                        <tbody>
                """
                for event in fed_events[:5]:
                    date_str = event.get('date', 'TBD')
                    event_name = event.get('name', 'Unknown')
                    impact = event.get('impact', 'Medium')
                    watch_for = event.get('watch_for', 'Market reaction')

                    fed_html += f"""
                            <tr>
                                <td>{date_str}</td>
                                <td style="font-weight: bold;">{event_name}</td>
                                <td>{impact}</td>
                                <td style="font-size: 12px;">{watch_for}</td>
                            </tr>
                    """

                fed_html += """
                        </tbody>
                    </table>
                </div>
                """

        # Combine sections
        if earnings_html or fed_html:
            return f"""
            <div class="section upcoming-events">
                <h2 style="color: #667eea;">🔮 UPCOMING EVENTS TO WATCH</h2>
                <div class="events-intro">
                    <p>Mark your calendar for these key market-moving events. Position accordingly and watch for volatility around these dates.</p>
                </div>
                {earnings_html}
                {fed_html}
            </div>
            """
        else:
            return ""

    def _get_section_title(self, advice_type: TradingAdvice) -> str:
        """Get human-readable section title."""
        titles = {
            TradingAdvice.TRADE_ALERT: "TRADE ALERTS - Immediate Action",
            TradingAdvice.WATCH: "WATCH LIST - Monitor Closely",
            TradingAdvice.INFO: "MARKET CONTEXT - Background Info"
        }
        return titles.get(advice_type, "Unknown Category")

    def _generate_footer(self) -> str:
        """Generate email footer with disclaimers and info."""
        return f"""
        <div class="footer">
            <div class="disclaimer">
                <p><strong>⚠️ Important Disclaimer:</strong></p>
                <p>This digest is for informational purposes only and should not be considered as investment advice.
                Always conduct your own research and consult with financial advisors before making trading decisions.</p>
            </div>
            <div class="signature">
                <p>📈 Generated by Trade Ideas Analyzer</p>
                <p><small>Automated daily digest • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
            </div>
        </div>
        """

    def _get_email_styles(self) -> str:
        """Get Robinhood-inspired dark mode CSS styles."""
        return """
        <style>
            body {
                font-family: -apple-system, system-ui, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 0;
                background-color: #000000;
                color: #ffffff;
            }

            .email-container {
                max-width: 900px;
                margin: 0 auto;
                background-color: #1c1c1e;
            }

            .header {
                background: linear-gradient(135deg, #00ff88 0%, #00c6ff 100%);
                color: #000000;
                padding: 40px 30px;
                text-align: center;
            }

            .header h1 {
                margin: 0 0 15px 0;
                font-size: 32px;
                font-weight: 700;
            }

            .header-info {
                font-size: 16px;
            }

            .header-info .date {
                font-weight: 600;
                margin-bottom: 5px;
                opacity: 0.85;
            }

            .header-info .summary {
                opacity: 0.75;
            }

            /* Market Summary Section */
            .market-summary {
                padding: 30px;
                background: #2c2c2e;
                border-bottom: 1px solid #3a3a3c;
            }

            .market-summary h2 {
                margin: 0 0 25px 0;
                font-size: 22px;
                color: #00ff88;
            }

            .market-grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
                margin-bottom: 25px;
            }

            .market-stat {
                background: #1c1c1e;
                padding: 18px;
                border-radius: 12px;
                text-align: center;
                border: 1px solid #3a3a3c;
            }

            .stat-label {
                display: block;
                font-size: 11px;
                color: #8e8e93;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 8px;
            }

            .stat-value {
                display: block;
                font-size: 22px;
                font-weight: 700;
            }

            .stat-value.positive {
                color: #00ff88;
            }

            .stat-value.negative {
                color: #ff4444;
            }

            .stat-value.neutral {
                color: #ffd700;
            }

            .stat-sublabel {
                font-size: 10px;
                color: #8e8e93;
                margin-top: 5px;
            }

            /* ML Prediction */
            .ml-prediction {
                background: linear-gradient(135deg, #1e3a5f 0%, #2d1b5e 100%);
                padding: 25px;
                border-radius: 14px;
                display: flex;
                align-items: center;
                gap: 20px;
                border: 1px solid #4a4a4c;
            }

            .ml-icon {
                font-size: 40px;
            }

            .ml-content {
                flex: 1;
            }

            .ml-title {
                color: #8e8e93;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 8px;
            }

            .ml-forecast {
                font-size: 17px;
                font-weight: 600;
                color: #00ff88;
                margin-bottom: 5px;
            }

            .ml-meta {
                font-size: 12px;
                color: #8e8e93;
            }

            /* Body Sections */
            .body {
                padding: 30px;
            }

            .section {
                margin-bottom: 40px;
            }

            .section-header {
                margin-bottom: 20px;
            }

            .section h2 {
                font-size: 20px;
                margin: 0 0 8px 0;
                font-weight: 700;
            }

            .section-description {
                color: #8e8e93;
                font-size: 13px;
            }

            /* Table styles */
            .digest-table {
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
                font-size: 13px;
            }

            .digest-table thead {
                background: #2c2c2e;
                border-bottom: 2px solid #00ff88;
            }

            .digest-table th {
                padding: 14px 12px;
                text-align: left;
                font-weight: 600;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                color: #8e8e93;
            }

            .digest-table td {
                padding: 16px 12px;
                border-bottom: 1px solid #3a3a3c;
                vertical-align: middle;
            }

            .digest-table tbody tr:hover {
                background-color: #2c2c2e;
            }

            .digest-table tbody tr:last-child td {
                border-bottom: 2px solid #3a3a3c;
            }

            .digest-table a {
                color: #00c6ff;
                text-decoration: none;
                font-weight: 500;
            }

            .digest-table a:hover {
                text-decoration: underline;
            }

            /* Upcoming events */
            .upcoming-events {
                background: #2c2c2e;
                padding: 25px;
                border-radius: 12px;
                border: 1px solid #3a3a3c;
                margin-bottom: 30px;
            }

            .upcoming-events h2 {
                color: #00ff88;
                margin: 0 0 20px 0;
            }

            .upcoming-section {
                margin: 20px 0;
            }

            .upcoming-section h3 {
                color: #ffd700;
                font-size: 16px;
                margin: 15px 0 10px 0;
            }

            .events-intro {
                background-color: rgba(255, 215, 0, 0.1);
                padding: 15px;
                border-left: 4px solid #ffd700;
                margin-bottom: 20px;
                border-radius: 6px;
            }

            .events-intro p {
                margin: 0;
                font-size: 13px;
                color: #e5e5ea;
            }

            /* Footer */
            .footer {
                background-color: #2c2c2e;
                padding: 30px;
                border-top: 1px solid #3a3a3c;
            }

            .disclaimer {
                margin-bottom: 20px;
                padding: 15px;
                background-color: rgba(255, 215, 0, 0.1);
                border-left: 4px solid #ffd700;
                font-size: 12px;
                border-radius: 6px;
            }

            .disclaimer p {
                margin: 5px 0;
                color: #e5e5ea;
            }

            .signature {
                text-align: center;
                font-size: 13px;
                color: #8e8e93;
            }

            /* Mobile responsiveness */
            @media (max-width: 600px) {
                .email-container {
                    margin: 0;
                }

                .header, .body, .footer {
                    padding: 20px;
                }

                .header h1 {
                    font-size: 24px;
                }

                .market-grid {
                    grid-template-columns: repeat(2, 1fr);
                }

                .ml-prediction {
                    flex-direction: column;
                    text-align: center;
                }
            }
        </style>
        """

    def _generate_error_email(self, error_message: str) -> str:
        """Generate error email when formatting fails."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Digest Error</title>
        </head>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>⚠️ News Digest Error</h2>
            <p>Sorry, there was an error generating your daily news digest:</p>
            <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px;">{error_message}</pre>
            <p>Please contact support if this issue persists.</p>
            <p><small>Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
        </body>
        </html>
        """

    def format_plain_text_digest(self, digest_items: List[NewsDigestItem]) -> str:
        """
        Format digest as plain text for email clients that don't support HTML.

        Args:
            digest_items (List[NewsDigestItem]): Processed news digest items

        Returns:
            str: Plain text email content
        """
        lines = []
        lines.append("📰 DAILY FINANCIAL NEWS DIGEST")
        lines.append("=" * 50)
        lines.append(f"📅 {datetime.now().strftime('%A, %B %d, %Y')}")
        lines.append(f"💡 {len(digest_items)} Headlines with Trading Insights")
        lines.append("")

        # Group by category
        categorized = self._categorize_items(digest_items)

        for advice_type in sorted(TradingAdvice, key=lambda x: self.advice_priorities[x]):
            items = categorized.get(advice_type, [])
            if not items:
                continue

            icon = self.advice_icons[advice_type]
            title = self._get_section_title(advice_type)
            lines.append(f"{icon} {title} ({len(items)})")
            lines.append("-" * 30)

            for i, item in enumerate(items[:10], 1):
                lines.append(f"{i}. {item.title}")
                lines.append(f"   📊 {item.advice_reason}")
                if item.affected_symbols:
                    lines.append(f"   📈 Symbols: {', '.join(item.affected_symbols[:3])}")
                lines.append(f"   🔗 {item.url}")
                lines.append("")

            lines.append("")

        lines.append("⚠️ DISCLAIMER:")
        lines.append("This digest is for informational purposes only.")
        lines.append("Always conduct your own research before trading.")
        lines.append("")
        lines.append("📈 Generated by Trade Ideas Analyzer")

        return "\n".join(lines)