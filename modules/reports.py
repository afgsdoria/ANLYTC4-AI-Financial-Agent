from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)

from reportlab.lib import colors
from reportlab.lib.styles import (
    getSampleStyleSheet
)

from reportlab.lib.pagesizes import letter


def generate_financial_report(
    username,
    advice,
    score,
    level,
    recommendations,
    alerts,
    monthly_income,
    total_spending,
    current_savings,
    savings_goal,
    goal_name=None,
    target_amount=None,
    deadline=None
):

    filename = (
        f"{username}_financial_report.pdf"
    )

    doc = SimpleDocTemplate(
        filename,
        pagesize=letter
    )

    styles = getSampleStyleSheet()

    elements = []

    # ==================================
    # TITLE
    # ==================================

    title = Paragraph(
        "💰 <b>Financial AI Agent Report</b>",
        styles["Title"]
    )

    elements.append(title)

    elements.append(
        Paragraph(
            f"Generated for: <b>{username}</b>",
            styles["Heading3"]
        )
    )

    elements.append(Spacer(1, 15))

    # ==================================
    # USER SUMMARY
    # ==================================

    elements.append(
        Paragraph(
            "📌 Financial Summary",
            styles["Heading2"]
        )
    )

    summary_data = [
        ["Category", "Value"],
        ["Monthly Income", f"₱{monthly_income:,.2f}"],
        ["Total Spending", f"₱{total_spending:,.2f}"],
        ["Current Savings", f"₱{current_savings:,.2f}"],
        ["Savings Goal", f"₱{savings_goal:,.2f}"],
        ["Health Score", f"{score}/100"],
        ["Financial Status", level]
    ]

    summary_table = Table(
        summary_data,
        colWidths=[220, 220]
    )

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10)
    ]))

    elements.append(summary_table)

    elements.append(Spacer(1, 20))

    # ==================================
    # GOAL SECTION
    # ==================================

    elements.append(
        Paragraph(
            "🎯 Financial Goal",
            styles["Heading2"]
        )
    )

    if goal_name:

        goal_text = f"""
        <b>Goal:</b> {goal_name}<br/>
        <b>Target Amount:</b>
        ₱{target_amount:,.2f}<br/>
        <b>Deadline:</b>
        {deadline}
        """

    else:

        goal_text = (
            "No financial goal set."
        )

    elements.append(
        Paragraph(
            goal_text,
            styles["BodyText"]
        )
    )

    elements.append(Spacer(1, 20))

    # ==================================
    # ALERTS
    # ==================================

    elements.append(
        Paragraph(
            "🚨 AI Spending Alerts",
            styles["Heading2"]
        )
    )

    if alerts:

        for alert in alerts:

            elements.append(
                Paragraph(
                    f"• {alert}",
                    styles["BodyText"]
                )
            )

    else:

        elements.append(
            Paragraph(
                "No spending risks detected.",
                styles["BodyText"]
            )
        )

    elements.append(Spacer(1, 20))

    # ==================================
    # RECOMMENDATIONS
    # ==================================

    elements.append(
        Paragraph(
            "💡 Smart Recommendations",
            styles["Heading2"]
        )
    )

    for recommendation in recommendations:

        elements.append(
            Paragraph(
                f"• {recommendation}",
                styles["BodyText"]
            )
        )

    elements.append(Spacer(1, 20))

    # ==================================
    # AI ANALYSIS
    # ==================================

    elements.append(
        Paragraph(
            "🤖 AI Financial Analysis",
            styles["Heading2"]
        )
    )

    elements.append(
        Paragraph(
            advice,
            styles["BodyText"]
        )
    )

    elements.append(Spacer(1, 20))

    # ==================================
    # FOOTER
    # ==================================

    elements.append(
        Paragraph(
            "Generated using Financial AI Agent",
            styles["Italic"]
        )
    )

    doc.build(elements)

    return filename