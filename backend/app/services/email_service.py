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

        # Determine trend color
        if 'BULLISH' in market_trend:
            trend_color = "#00ff88"
        elif 'BEARISH' in market_trend:
            trend_color = "#ff4444"
        else:
            trend_color = "#ffd700"

        # Generate index stats HTML with proper ordering (SPY, QQQ, DIA)
        index_order = ['SPY', 'QQQ', 'DIA']
        index_stats_html = ""
        for symbol in index_order:
            if symbol in major_indices:
                data = major_indices[symbol]
                level = data.get('level', 0)
                change = data.get('change', '+0.0%')
                change_color = "#00ff88" if change.startswith('+') else "#ff4444" if change.startswith('-') else "#8e8e93"

                index_stats_html += f"""
                    <div class="market-stat">
                        <div class="stat-label">{symbol}</div>
                        <div class="stat-value">{level:.2f}</div>
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

            row = f"""
            <tr>
                <td style="text-align: center;">{idx}</td>
                <td><strong>{item.title}</strong><br/><small>{item.summary}</small></td>
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
