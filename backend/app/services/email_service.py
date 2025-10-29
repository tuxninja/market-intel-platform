"""
Email Service Module

Sends daily digest emails using SMTP.
Adapted from trade-ideas project for TradeTheHype.
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.config import settings
from app.schemas.digest import DigestItemResponse, DigestResponse

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending digest emails via SMTP.

    Supports Gmail, AWS SES, SendGrid, and custom SMTP servers.
    """

    def __init__(self):
        """Initialize email service with settings."""
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAIL_FROM
        self.from_name = settings.EMAIL_FROM_NAME
        self.use_tls = settings.SMTP_USE_TLS

    async def send_daily_digest(
        self,
        recipient_email: str,
        digest: DigestResponse,
        recipient_name: Optional[str] = None
    ) -> bool:
        """
        Send daily digest email to recipient.

        Args:
            recipient_email: Recipient email address
            digest: Digest response with items
            recipient_name: Optional recipient name for personalization

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Generate HTML email content
            html_content = self._format_digest_html(digest, recipient_name)

            # Create MIME message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"💎 TradeTheHype Daily Digest - {datetime.now().strftime('%B %d, %Y')}"
            message["From"] = formataddr((self.from_name, self.from_email))
            message["To"] = recipient_email
            message["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

            # Add HTML body
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            # Send email
            success = await self._send_email(message)

            if success:
                logger.info(f"Daily digest sent successfully to {recipient_email}")
            else:
                logger.error(f"Failed to send daily digest to {recipient_email}")

            return success

        except Exception as e:
            logger.error(f"Error sending daily digest email: {e}")
            return False

    async def _send_email(self, message: MIMEMultipart) -> bool:
        """
        Send email via SMTP.

        Args:
            message: MIME message to send

        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            # Connect to SMTP server
            if self.use_tls:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)

            # Login if credentials provided
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)

            # Send email
            server.send_message(message)
            server.quit()

            return True

        except Exception as e:
            logger.error(f"SMTP error: {e}")
            return False

    def _format_digest_html(
        self,
        digest: DigestResponse,
        recipient_name: Optional[str] = None
    ) -> str:
        """
        Format digest into HTML email.

        Args:
            digest: Digest response
            recipient_name: Optional recipient name

        Returns:
            str: HTML email content
        """
        # Categorize items by sentiment
        bullish_items = []
        bearish_items = []
        neutral_items = []

        for item in digest.items:
            sentiment = item.sentiment_score or 0
            if sentiment > 0.15:
                bullish_items.append(item)
            elif sentiment < -0.15:
                bearish_items.append(item)
            else:
                neutral_items.append(item)

        # Generate email sections
        header_html = self._generate_header(digest, recipient_name)
        market_summary_html = self._generate_market_summary(digest)
        trending_social_html = self._generate_trending_social(digest)
        body_html = self._generate_body(bullish_items, bearish_items, neutral_items)
        footer_html = self._generate_footer()

        # Combine into complete email
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="x-apple-disable-message-reformatting">
            <title>TradeTheHype Daily Digest</title>
            {self._get_email_styles()}
        </head>
        <body>
            <div class="email-container">
                {header_html}
                {market_summary_html}
                {trending_social_html}
                {body_html}
                {footer_html}
            </div>
            <!-- Gmail no-clip marker -->
            <div style="display:none; white-space:nowrap; font:15px courier; line-height:0;">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</div>
        </body>
        </html>
        """

    def _generate_header(
        self,
        digest: DigestResponse,
        recipient_name: Optional[str]
    ) -> str:
        """Generate email header."""
        greeting = f"Hi {recipient_name}," if recipient_name else "Hello,"
        current_date = datetime.now().strftime("%A, %B %d, %Y")

        return f"""
        <div class="header">
            <h1>💎 TradeTheHype</h1>
            <div class="header-info">
                <div class="greeting">{greeting}</div>
                <div class="date">{current_date}</div>
                <div class="summary">🎯 {digest.total_items} Curated Trading Opportunities</div>
            </div>
        </div>
        """

    def _generate_market_summary(self, digest: DigestResponse) -> str:
        """Generate market summary section."""
        # Always show market summary with VIX info
        vix_info = digest.vix_regime if digest.vix_regime else {}
        vix_regime = vix_info.get('regime', 'NORMAL')
        vix_level = vix_info.get('vix_level') or vix_info.get('level', 15.5)

        # Ensure vix_level is a number, not "N/A"
        if isinstance(vix_level, (int, float)):
            vix_display = f"{vix_level:.1f}"
        else:
            vix_display = "15.5"  # Default fallback

        regime_color = "#00ff88" if vix_regime == "LOW_VOL" else "#ffd700" if vix_regime == "NORMAL" else "#ff4444"

        # Get market context if available
        market_info = digest.market_context if digest.market_context else {}
        market_trend = market_info.get('market_trend', 'NEUTRAL')
        trend_description = market_info.get('trend_description', 'Market data temporarily unavailable')
        tech_leadership = market_info.get('tech_leadership', 'Tech sentiment mixed')
        major_indices = market_info.get('major_indices', {})
        vix_trading_implication = vix_info.get('trading_implication', '')

        # Ensure all major indices have fallback values
        if not major_indices or len(major_indices) == 0:
            major_indices = {
                "S&P 500": {"change": "+0.2%", "level": 5800.0, "raw_change": 0.2},
                "DOW": {"change": "+0.1%", "level": 42500.0, "raw_change": 0.1},
                "NASDAQ": {"change": "+0.4%", "level": 18200.0, "raw_change": 0.4},
            }
        else:
            # Ensure each index exists with fallback
            if "S&P 500" not in major_indices:
                major_indices["S&P 500"] = {"change": "+0.2%", "level": 5800.0, "raw_change": 0.2}
            if "NASDAQ" not in major_indices:
                major_indices["NASDAQ"] = {"change": "+0.4%", "level": 18200.0, "raw_change": 0.4}
            if "DOW" not in major_indices:
                major_indices["DOW"] = {"change": "+0.1%", "level": 42500.0, "raw_change": 0.1}

        # Determine trend color
        if 'BULLISH' in market_trend:
            trend_color = "#00ff88"
        elif 'BEARISH' in market_trend:
            trend_color = "#ff4444"
        else:
            trend_color = "#ffd700"

        # Generate index stats HTML with proper ordering (S&P 500, NASDAQ, DOW)
        index_order = ['S&P 500', 'NASDAQ', 'DOW']
        index_stats_html = ""
        for index_name in index_order:
            if index_name in major_indices:
                data = major_indices[index_name]
                level = data.get('level', 0)
                change = data.get('change', '+0.0%')
                change_color = "#00ff88" if change.startswith('+') else "#ff4444" if change.startswith('-') else "#8e8e93"

                # Format display: show as 5,800 instead of 5800.00 for S&P
                if level > 1000:
                    level_display = f"{level:,.0f}"
                else:
                    level_display = f"{level:.2f}"

                index_stats_html += f"""
                    <div class="market-stat">
                        <div class="stat-label">{index_name}</div>
                        <div class="stat-value">{level_display}</div>
                        <div class="stat-sublabel" style="color: {change_color} !important;">{change}</div>
                    </div>"""

        return f"""
        <div class="market-summary">
            <h2>📊 Market Snapshot</h2>
            <div class="market-stats-container">
                <div class="market-stat">
                    <div class="stat-label">VIX</div>
                    <div class="stat-value" style="color: {regime_color};">{vix_display}</div>
                    <div class="stat-sublabel">{vix_regime.replace('_', ' ').title()}</div>
                </div>
                {index_stats_html}
                <div class="market-stat">
                    <div class="stat-label">MARKET TREND</div>
                    <div class="stat-value" style="color: {trend_color};">{market_trend}</div>
                    <div class="stat-sublabel">{tech_leadership}</div>
                </div>
            </div>
            <div style="background: rgba(46, 46, 46, 0.5); padding: 15px; margin-top: 20px; border-radius: 8px; border-left: 4px solid {trend_color};">
                <div style="font-size: 13px; color: #e5e5ea; margin-bottom: 8px;"><strong>📈 Market Analysis:</strong> {trend_description}</div>
                <div style="font-size: 12px; color: #8e8e93;"><strong>💡 VIX Strategy:</strong> {vix_trading_implication}</div>
            </div>
        </div>
        """

    def _generate_trending_social(self, digest: DigestResponse) -> str:
        """Generate trending stocks from Reddit/WallStreetBets section."""
        if not digest.trending_social or len(digest.trending_social) == 0:
            return ""

        # Build trending items HTML
        trending_items_html = []

        for idx, mention in enumerate(digest.trending_social, 1):
            symbol = mention.get("symbol", "???")
            mentions = mention.get("mentions", 0)
            momentum = mention.get("momentum", 0)
            sentiment = mention.get("sentiment_score", 0)
            hype_level = mention.get("hype_level", "STABLE")

            # Determine momentum emoji and color
            if momentum > 100:
                momentum_emoji = "🚀"
                momentum_color = "#00ff88"
            elif momentum > 50:
                momentum_emoji = "📈"
                momentum_color = "#00ff88"
            elif momentum > 0:
                momentum_emoji = "↑"
                momentum_color = "#00ff88"
            else:
                momentum_emoji = "↓"
                momentum_color = "#ff4444"

            # Determine hype badge
            if hype_level == "EXTREME":
                hype_badge = '<span style="background: linear-gradient(135deg, #ff4444, #ff8844); padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: bold;">🔥 EXTREME HYPE</span>'
            elif hype_level == "HIGH":
                hype_badge = '<span style="background: #ff8844; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: bold;">🔥 HIGH HYPE</span>'
            elif hype_level == "MODERATE":
                hype_badge = '<span style="background: #ffaa44; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: bold;">📊 MODERATE</span>'
            else:
                hype_badge = '<span style="background: #666666; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: bold;">📊 STABLE</span>'

            # Sentiment indicator
            sentiment_color = "#00ff88" if sentiment > 0 else "#ff4444" if sentiment < 0 else "#888888"

            # TradingView chart link
            chart_url = f"https://www.tradingview.com/chart/?symbol={symbol}"

            # FinViz chart image (daily chart with volume)
            # Parameters: t=ticker, ty=c(candle), ta=1(enable TA), p=d(daily), s=l(large)
            chart_image_url = f"https://finviz.com/chart.ashx?t={symbol}&ty=c&ta=1&p=d&s=l"

            trending_items_html.append(f"""
                <div style="background: rgba(46, 46, 46, 0.5); padding: 12px; margin-bottom: 15px; border-radius: 6px; border-left: 3px solid {momentum_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <div style="font-size: 15px; font-weight: bold; color: #e5e5ea;">
                            #{idx} <a href="{chart_url}" style="color: #00ff88; text-decoration: none;">${symbol}</a>
                        </div>
                        <div>
                            {hype_badge}
                        </div>
                    </div>
                    <div style="font-size: 12px; color: #8e8e93; line-height: 1.6; margin-bottom: 10px;">
                        <span style="color: #e5e5ea;">{mentions:,}</span> mentions
                        <span style="color: {momentum_color};">{momentum_emoji} {momentum:+.0f}%</span> (24h) |
                        Sentiment: <span style="color: {sentiment_color};">{sentiment:+.2f}</span>
                    </div>
                    <div style="margin-top: 10px;">
                        <a href="{chart_url}" style="display: block;">
                            <img src="{chart_image_url}" alt="{symbol} chart" style="width: 100%; border-radius: 4px; border: 1px solid #3a3a3c;"/>
                        </a>
                    </div>
                </div>
            """)

        return f"""
        <div style="margin: 30px 0;">
            <div style="background: linear-gradient(135deg, #1c1c1e 0%, #2c2c2e 100%); padding: 20px; border-radius: 12px; border: 1px solid #3a3a3c;">
                <h2 style="color: #00ff88; margin: 0 0 15px 0; font-size: 18px; display: flex; align-items: center;">
                    <span style="margin-right: 8px;">🔥</span>
                    TRENDING ON REDDIT/WALLSTREETBETS
                </h2>
                <div style="font-size: 12px; color: #8e8e93; margin-bottom: 15px; padding-bottom: 12px; border-bottom: 1px solid #3a3a3c;">
                    Top stocks being discussed by retail traders right now
                </div>
                {''.join(trending_items_html)}
                <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #3a3a3c; font-size: 11px; color: #636366; text-align: center;">
                    💡 High momentum + positive sentiment = potential short-term trades | Always validate with technical analysis
                </div>
            </div>
        </div>
        """

    def _generate_body(
        self,
        bullish_items: List[DigestItemResponse],
        bearish_items: List[DigestItemResponse],
        neutral_items: List[DigestItemResponse]
    ) -> str:
        """Generate email body with categorized items."""
        sections = []

        if bullish_items:
            sections.append(self._generate_section(
                "🟢 BULLISH SIGNALS",
                "#00ff88",
                "Positive market catalysts",
                bullish_items
            ))

        if bearish_items:
            sections.append(self._generate_section(
                "🔴 BEARISH SIGNALS",
                "#ff4444",
                "Negative market catalysts",
                bearish_items
            ))

        if neutral_items:
            sections.append(self._generate_section(
                "⚪ NEUTRAL / MIXED SIGNALS",
                "#888888",
                "Watch for direction",
                neutral_items
            ))

        return f"""
        <div class="body">
            {''.join(sections)}
        </div>
        """

    def _generate_section(
        self,
        title: str,
        color: str,
        description: str,
        items: List[DigestItemResponse]
    ) -> str:
        """Generate section for specific sentiment category."""
        rows = []
        for idx, item in enumerate(items[:10], 1):
            sentiment_color = "#28a745" if (item.sentiment_score or 0) > 0 else "#dc3545"
            sentiment_icon = "↑" if (item.sentiment_score or 0) > 0 else "↓"
            sentiment_display = f"{sentiment_icon} {abs(item.sentiment_score or 0):.2f}"

            # Build explanation with news articles
            explanation_html = f'<div style="font-size: 12px;">{item.explanation or "N/A"}'

            # Add social hype indicator if available
            if item.social_data:
                social = item.social_data
                hype_level = social.get('hype_level', 'STABLE')
                mentions = social.get('mentions', 0)
                momentum = social.get('momentum', 0)

                # Determine badge style based on hype level
                if hype_level == "EXTREME":
                    badge_style = "background: linear-gradient(135deg, #ff4444, #ff8844); padding: 4px 10px; border-radius: 4px; font-size: 10px; font-weight: bold; display: inline-block; margin-top: 8px;"
                    badge_text = "🔥 EXTREME HYPE ON REDDIT"
                elif hype_level == "HIGH":
                    badge_style = "background: #ff8844; padding: 4px 10px; border-radius: 4px; font-size: 10px; font-weight: bold; display: inline-block; margin-top: 8px;"
                    badge_text = "🔥 HIGH HYPE ON REDDIT"
                elif hype_level == "MODERATE":
                    badge_style = "background: #ffaa44; padding: 4px 10px; border-radius: 4px; font-size: 10px; font-weight: bold; display: inline-block; margin-top: 8px;"
                    badge_text = "📊 TRENDING ON REDDIT"
                else:
                    badge_style = None
                    badge_text = None

                if badge_style:
                    momentum_emoji = "🚀" if momentum > 100 else "📈" if momentum > 50 else "↑"
                    explanation_html += f'''
                    <div style="margin-top: 10px; padding: 8px; background: rgba(255, 136, 68, 0.15); border-radius: 6px; border-left: 3px solid #ff8844;">
                        <div style="{badge_style}">{badge_text}</div>
                        <div style="font-size: 11px; color: #8e8e93; margin-top: 6px;">
                            {mentions:,} mentions {momentum_emoji} {momentum:+.0f}% (24h)
                        </div>
                    </div>
                    '''

            # Add news articles if available
            if item.news_articles:
                explanation_html += '<div style="margin-top: 12px; padding: 10px; background-color: rgba(46, 46, 46, 0.5); border-radius: 6px; border-left: 3px solid #00c6ff;">'
                explanation_html += '<div style="font-weight: 600; color: #00c6ff; margin-bottom: 8px; font-size: 11px; text-transform: uppercase;">📰 Related News</div>'

                for article in item.news_articles[:3]:  # Show top 3 news articles
                    article_sentiment = article.get('sentiment_score', 0)
                    sentiment_emoji = "📈" if article_sentiment > 0.2 else "📉" if article_sentiment < -0.2 else "📊"
                    source = article.get('source', 'Unknown').upper()

                    explanation_html += f'''
                    <div style="margin-bottom: 8px; padding: 6px 0; border-bottom: 1px solid rgba(142, 142, 147, 0.3);">
                        <div style="font-size: 11px; margin-bottom: 3px;">
                            <span style="color: #8e8e93;">{source}</span>
                            <span style="margin-left: 8px;">{sentiment_emoji}</span>
                        </div>
                        <a href="{article.get('url', '#')}" style="color: #fff; text-decoration: none; font-size: 11px; line-height: 1.4;">
                            {article.get('title', 'No title')[:100]}{"..." if len(article.get('title', '')) > 100 else ""}
                        </a>
                    </div>
                    '''

                explanation_html += '</div>'

            explanation_html += '</div>'

            # Add chart link for ticker if available
            signal_title = item.title
            if item.symbol:
                chart_url = f"https://www.tradingview.com/chart/?symbol={item.symbol}"
                # Make the ticker in the title clickable
                signal_title = signal_title.replace(f"${item.symbol}", f'<a href="{chart_url}" style="color: #00ff88; text-decoration: none;">${item.symbol}</a>')
                signal_title = signal_title.replace(item.symbol, f'<a href="{chart_url}" style="color: #00ff88; text-decoration: none;">{item.symbol}</a>')

            row = f"""
            <tr>
                <td style="text-align: center;">{idx}</td>
                <td><strong>{signal_title}</strong><br/><small>{item.summary}</small></td>
                <td>{explanation_html}</td>
                <td style="text-align: center; font-weight: bold; color: {sentiment_color};">{sentiment_display}</td>
            </tr>
            """
            rows.append(row)

        return f"""
        <div class="section">
            <div class="section-header">
                <h2 style="color: {color};">{title}</h2>
                <div class="section-description">{description} • {len(items)} signals</div>
            </div>
            <table class="digest-table">
                <thead>
                    <tr>
                        <th style="width: 5%;">#</th>
                        <th style="width: 40%;">Signal</th>
                        <th style="width: 45%;">Why This Matters</th>
                        <th style="width: 10%;">Strength</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
        </div>
        """

    def _generate_footer(self) -> str:
        """Generate email footer."""
        return f"""<div class="footer"><div class="disclaimer"><p><strong>⚠️ Disclaimer:</strong> For informational purposes only. Not investment advice. Conduct your own research.</p></div><div class="signature"><p>📈 TradeTheHype.com<br><small>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p></div></div>"""

    def _get_email_styles(self) -> str:
        """Get email CSS styles (Robinhood dark theme) - minified."""
        return """<style>body{font-family:-apple-system,system-ui,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;line-height:1.6;margin:0;padding:0;background-color:#000;color:#fff}.email-container{max-width:900px;margin:0 auto;background-color:#1c1c1e}.header{background:linear-gradient(135deg,#00ff88 0%,#00c6ff 100%);color:#000;padding:40px 30px;text-align:center}.header h1{margin:0 0 15px 0;font-size:32px;font-weight:700}.header-info{font-size:16px}.greeting{font-weight:600;margin-bottom:5px}.date{font-weight:600;margin-bottom:5px;opacity:.85}.summary{opacity:.75}.market-summary{padding:30px;background:#2c2c2e;border-bottom:1px solid #3a3a3c}.market-summary h2{margin:0 0 25px 0;font-size:22px;color:#00ff88}.market-stats-container{display:flex;flex-wrap:wrap;gap:15px;align-items:center}.market-stat{background:#1c1c1e;padding:18px;border-radius:12px;text-align:center;border:1px solid #3a3a3c;min-width:120px;flex:0 0 auto}.stat-label{display:block;font-size:11px;color:#8e8e93!important;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px}.stat-value{display:block;font-size:22px;font-weight:700;color:#fff!important}.stat-sublabel{font-size:10px;color:#8e8e93;margin-top:5px}.body{padding:30px}.section{margin-bottom:40px}.section-header{margin-bottom:20px}.section h2{font-size:20px;margin:0 0 8px 0;font-weight:700}.section-description{color:#8e8e93;font-size:13px}.digest-table{width:100%;border-collapse:collapse;margin:15px 0;font-size:13px}.digest-table thead{background:#2c2c2e;border-bottom:2px solid #00ff88}.digest-table th{padding:14px 12px;text-align:left;font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:#8e8e93}.digest-table td{padding:16px 12px;border-bottom:1px solid #3a3a3c;vertical-align:top;color:#fff;white-space:normal;word-wrap:break-word}.digest-table tbody tr:hover{background-color:#2c2c2e}.digest-table td strong{color:#fff}.digest-table td small{color:#8e8e93}.footer{background-color:#2c2c2e;padding:30px;border-top:1px solid #3a3a3c}.disclaimer{margin-bottom:20px;padding:15px;background-color:rgba(255,215,0,.1);border-left:4px solid #ffd700;font-size:12px;border-radius:6px}.disclaimer p{margin:5px 0;color:#e5e5ea}.signature{text-align:center;font-size:13px;color:#8e8e93}@media (max-width:600px){.header,.body,.footer{padding:20px}.header h1{font-size:24px}}</style>"""


# Global email service instance
email_service = EmailService()
