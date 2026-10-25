import html

CSS = """
<style>
footer {visibility: hidden;}
.block-container {padding-top: 2rem;}

.hero {
    padding: 1.6rem 1.8rem;
    border-radius: 16px;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    margin-bottom: 1.2rem;
}
.hero h1 {margin: 0; font-size: 2rem; color: #ffffff;}
.hero p {margin: 0.4rem 0 0; color: #e0e7ff; font-size: 1rem;}

.score-card {
    border: 1px solid rgba(128, 128, 128, 0.3);
    border-radius: 16px;
    padding: 1.2rem 1rem;
    text-align: center;
    background: rgba(128, 128, 128, 0.07);
    height: 100%;
}
.score-title {font-size: 0.9rem; opacity: 0.75; margin-bottom: 0.2rem;}
.score-value {font-size: 2.6rem; font-weight: 700; line-height: 1.2;}
.score-sub {font-size: 0.8rem; opacity: 0.7; margin-top: 0.3rem;}
.bar-bg {height: 8px; border-radius: 999px; background: rgba(128, 128, 128, 0.25); margin-top: 0.6rem;}
.bar-fill {height: 8px; border-radius: 999px;}

.chip {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    margin: 0.2rem 0.2rem 0.2rem 0;
    border-radius: 999px;
    font-size: 0.85rem;
    border: 1px solid;
}
.chip-green {background: rgba(34, 197, 94, 0.15); color: #16a34a; border-color: rgba(34, 197, 94, 0.5);}
.chip-red {background: rgba(239, 68, 68, 0.15); color: #dc2626; border-color: rgba(239, 68, 68, 0.5);}
.chip-blue {background: rgba(59, 130, 246, 0.15); color: #2563eb; border-color: rgba(59, 130, 246, 0.5);}

.check {
    border-left: 4px solid;
    border-radius: 8px;
    padding: 0.6rem 0.9rem;
    margin-bottom: 0.5rem;
    background: rgba(128, 128, 128, 0.07);
}
.check-ok {border-color: #22c55e;}
.check-bad {border-color: #ef4444;}
.check-title {font-weight: 600;}
.check-pts {float: right; opacity: 0.7; font-size: 0.85rem;}
.check-msg {font-size: 0.88rem; opacity: 0.85; margin-top: 0.15rem;}
</style>
"""

def score_color(value):
    if value >= 75:
        return "#22c55e"   # green
    if value >= 50:
        return "#f59e0b"   # orange
    return "#ef4444"       # red

def score_card(title, value, suffix, subtitle=""):
    color = score_color(value)
    width = max(0, min(100, value))
    return (
        '<div class="score-card">'
        f'<div class="score-title">{html.escape(title)}</div>'
        f'<div class="score-value" style="color:{color}">{value}{suffix}</div>'
        f'<div class="bar-bg"><div class="bar-fill" style="width:{width}%; background:{color}"></div></div>'
        f'<div class="score-sub">{html.escape(subtitle)}</div>'
        '</div>'
    )

def chips(items, color, empty_text="None"):
    if not items:
        return f'<span style="opacity:0.7">{html.escape(empty_text)}</span>'
    return "".join(f'<span class="chip chip-{color}">{html.escape(i)}</span>' for i in items)

def check_row(label, earned, maximum, message, passed):
    state = "ok" if passed else "bad"
    icon = "✅" if passed else "❌"
    return (
        f'<div class="check check-{state}">'
        f'<span class="check-pts">{earned}/{maximum}</span>'
        f'<div class="check-title">{icon} {html.escape(label)}</div>'
        f'<div class="check-msg">{html.escape(message)}</div>'
        '</div>'
    )