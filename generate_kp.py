#!/usr/bin/env python3
"""Generate commercial proposal PDF for Place for Beauty."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os, datetime

OUT = "КП_Place_for_Beauty.pdf"

# Colors
DARK   = colors.HexColor("#0D0D0D")
GOLD   = colors.HexColor("#C9A84C")
LIGHT  = colors.HexColor("#F5F0E8")
GRAY   = colors.HexColor("#555555")
WHITE  = colors.white

W, H = A4

_FONT_CANDIDATES = [
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ("/usr/share/fonts/dejavu/DejaVuSans.ttf",
     "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"),
    ("C:/Windows/Fonts/arial.ttf",   "C:/Windows/Fonts/arialbd.ttf"),
    ("C:/Windows/Fonts/calibri.ttf", "C:/Windows/Fonts/calibrib.ttf"),
    ("/Library/Fonts/Arial.ttf",     "/Library/Fonts/Arial Bold.ttf"),
]

def register_fonts():
    for reg, bold in _FONT_CANDIDATES:
        if os.path.exists(reg):
            try:
                pdfmetrics.registerFont(TTFont("CyrFont",      reg))
                pdfmetrics.registerFont(TTFont("CyrFont-Bold",
                                               bold if os.path.exists(bold) else reg))
                return "CyrFont", "CyrFont-Bold"
            except Exception:
                continue
    return "Helvetica", "Helvetica-Bold"

FONT, FONT_BOLD = register_fonts()

def style(name, **kw):
    base = dict(fontName=FONT, fontSize=10, textColor=DARK,
                leading=14, spaceAfter=4)
    base.update(kw)
    return ParagraphStyle(name, **base)

S_TITLE   = style("title",  fontName=FONT_BOLD, fontSize=28, textColor=GOLD,
                  alignment=TA_CENTER, leading=34, spaceAfter=6)
S_SUBTITLE= style("sub",    fontName=FONT_BOLD, fontSize=13, textColor=DARK,
                  alignment=TA_CENTER, leading=18, spaceAfter=4)
S_DATE    = style("date",   fontSize=10, textColor=GRAY, alignment=TA_CENTER,
                  spaceAfter=20)
S_H2      = style("h2",     fontName=FONT_BOLD, fontSize=13, textColor=GOLD,
                  leading=18, spaceAfter=8, spaceBefore=14)
S_BODY    = style("body",   fontSize=10, textColor=DARK, leading=16,
                  spaceAfter=6)
S_SMALL   = style("small",  fontSize=9,  textColor=GRAY, leading=14)
S_FOOTER  = style("footer", fontSize=9,  textColor=GRAY, alignment=TA_CENTER)
S_RIGHT   = style("right",  fontSize=10, textColor=DARK, alignment=TA_RIGHT)
S_PRICE   = style("price",  fontName=FONT_BOLD, fontSize=22, textColor=GOLD,
                  alignment=TA_CENTER, leading=28)

def gold_line():
    return HRFlowable(width="100%", thickness=1.5, color=GOLD, spaceAfter=12)

def section_title(text):
    return Paragraph(text, S_H2)

def body(text):
    return Paragraph(text, S_BODY)

def build():
    doc = SimpleDocTemplate(
        OUT, pagesize=A4,
        leftMargin=2.2*cm, rightMargin=2.2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    story = []

    # ── ШАПКА ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("INTEGRA DEVELOP", S_TITLE))
    story.append(Paragraph("Разработка сайтов и digital-решений", S_SUBTITLE))
    story.append(Paragraph(
        f"Коммерческое предложение · {datetime.date.today().strftime('%d.%m.%Y')}",
        S_DATE
    ))
    story.append(gold_line())

    # ── КОМУ ────────────────────────────────────────────────────────────────
    story.append(section_title("Кому адресовано"))
    tbl = Table([
        ["Клиент:", "Place for Beauty — барбершоп"],
        ["Контакт:", "vk.com/placeforbeauty42"],
        ["Сайт:",    "193.164.150.235"],
    ], colWidths=[4*cm, 12*cm])
    tbl.setStyle(TableStyle([
        ("FONTNAME",    (0,0), (-1,-1), FONT),
        ("FONTNAME",    (0,0), (0,-1),  FONT_BOLD),
        ("FONTSIZE",    (0,0), (-1,-1), 10),
        ("TEXTCOLOR",   (0,0), (0,-1),  GOLD),
        ("TEXTCOLOR",   (1,0), (1,-1),  DARK),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [LIGHT, WHITE]),
        ("TOPPADDING",  (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.4*cm))

    # ── ЧТО СДЕЛАНО ─────────────────────────────────────────────────────────
    story.append(gold_line())
    story.append(section_title("Что было разработано"))
    story.append(body(
        "Для барбершопа <b>Place for Beauty</b> создан полноценный "
        "продающий сайт с уникальным дизайном в стиле «тёмная роскошь» — "
        "без шаблонов и конструкторов."
    ))

    features = [
        ["✦", "Дизайн",
         "Авторский dark/gold стиль, анимированные частицы, "
         "адаптив под мобильные устройства"],
        ["✦", "Прайс-лист",
         "Все категории и услуги из актуального прайса, "
         "интерактивные вкладки с фильтрацией"],
        ["✦", "Backend",
         "Python FastAPI + SQLite — быстрый, надёжный, не требует "
         "дорогостоящего хостинга"],
        ["✦", "Админ-панель",
         "Полный CRUD: добавление/редактирование/удаление услуг и "
         "категорий, JWT-авторизация"],
        ["✦", "PDF-руководство",
         "Инструкция по работе с админкой в PDF — готова к печати"],
        ["✦", "Автодеплой",
         "GitHub Actions CI/CD — сайт обновляется автоматически "
         "при каждом изменении кода"],
        ["✦", "VPS-сервер",
         "Nginx + systemd, сайт работает 24/7 без участия разработчика"],
    ]
    ftbl = Table(features, colWidths=[0.5*cm, 3.5*cm, 12*cm])
    ftbl.setStyle(TableStyle([
        ("FONTNAME",     (0,0), (-1,-1), FONT),
        ("FONTNAME",     (1,0), (1,-1),  FONT_BOLD),
        ("FONTSIZE",     (0,0), (-1,-1), 10),
        ("TEXTCOLOR",    (0,0), (0,-1),  GOLD),
        ("TEXTCOLOR",    (1,0), (1,-1),  DARK),
        ("TEXTCOLOR",    (2,0), (2,-1),  GRAY),
        ("VALIGN",       (0,0), (-1,-1), "TOP"),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [LIGHT, WHITE]),
        ("LEFTPADDING",  (0,0), (-1,-1), 6),
    ]))
    story.append(ftbl)

    # ── СТОИМОСТЬ ───────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.4*cm))
    story.append(gold_line())
    story.append(section_title("Стоимость"))

    price_rows = [
        ["Разработка сайта",
         "Дизайн, вёрстка, backend, БД, админка, PDF-гайд",
         "20 000 — 30 000 ₽"],
        ["Настройка хостинга",
         "VPS, Nginx, systemd, автодеплой через GitHub Actions",
         "5 000 — 7 000 ₽"],
        ["Техподдержка (1 мес.)",
         "Обновления, правки контента, мониторинг сервера",
         "от 3 000 ₽/мес"],
    ]
    ptbl = Table(
        [["Услуга", "Состав", "Цена"]] + price_rows,
        colWidths=[4.5*cm, 8.5*cm, 3*cm]
    )
    ptbl.setStyle(TableStyle([
        # Header
        ("BACKGROUND",   (0,0), (-1,0),  DARK),
        ("TEXTCOLOR",    (0,0), (-1,0),  GOLD),
        ("FONTNAME",     (0,0), (-1,0),  FONT_BOLD),
        ("FONTSIZE",     (0,0), (-1,0),  10),
        ("ALIGN",        (0,0), (-1,0),  "CENTER"),
        # Body
        ("FONTNAME",     (0,1), (-1,-1), FONT),
        ("FONTNAME",     (0,1), (0,-1),  FONT_BOLD),
        ("FONTSIZE",     (0,1), (-1,-1), 9),
        ("TEXTCOLOR",    (0,1), (-1,-1), DARK),
        ("TEXTCOLOR",    (2,1), (2,-1),  GOLD),
        ("FONTNAME",     (2,1), (2,-1),  FONT_BOLD),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [LIGHT, WHITE]),
        ("TOPPADDING",   (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0), (-1,-1), 6),
        ("LEFTPADDING",  (0,0), (-1,-1), 8),
        ("VALIGN",       (0,0), (-1,-1), "TOP"),
        ("GRID",         (0,0), (-1,-1), 0.5, colors.HexColor("#DDDDDD")),
    ]))
    story.append(ptbl)

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Итого: <b>25 000 — 40 000 ₽</b>  (зависит от финального объёма работ)",
        S_PRICE
    ))

    # ── ПОЧЕМУ МЫ ───────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.3*cm))
    story.append(gold_line())
    story.append(section_title("Почему Integra Develop"))

    reasons = [
        "Уникальный дизайн — не конструктор Tilda/Wix, а ручная разработка под бренд",
        "Быстрая скорость загрузки — FastAPI backend, оптимизированные ресурсы",
        "Простое управление — сам меняешь цены и услуги через удобную админку",
        "Автодеплой — нет необходимости звонить разработчику при каждом обновлении",
        "Гарантия работоспособности — сайт задеплоен и протестирован перед сдачей",
        "Техподдержка — всегда на связи, исправление багов в течение 24 часов",
    ]
    for r in reasons:
        story.append(Paragraph(f"✓  {r}", S_BODY))

    # ── СЛЕДУЮЩИЙ ШАГ ───────────────────────────────────────────────────────
    story.append(Spacer(1, 0.3*cm))
    story.append(gold_line())
    story.append(section_title("Следующий шаг"))
    story.append(body(
        "Свяжитесь с нами для обсуждения деталей. После согласования "
        "подписываем договор, вносится предоплата 50% — работа начинается "
        "в течение 1-2 рабочих дней. Срок сдачи: 5–10 рабочих дней."
    ))

    # ── КОНТАКТЫ ────────────────────────────────────────────────────────────
    ctbl = Table([
        ["Разработчик:",  "Сергей Гусев — Integra Develop"],
        ["Email:",        "gusiev20033@gmail.com"],
        ["GitHub:",       "github.com/SergeyGusev1"],
    ], colWidths=[3.5*cm, 12.5*cm])
    ctbl.setStyle(TableStyle([
        ("FONTNAME",     (0,0), (-1,-1), FONT),
        ("FONTNAME",     (0,0), (0,-1),  FONT_BOLD),
        ("FONTSIZE",     (0,0), (-1,-1), 10),
        ("TEXTCOLOR",    (0,0), (0,-1),  GOLD),
        ("TEXTCOLOR",    (1,0), (1,-1),  DARK),
        ("BACKGROUND",   (0,0), (-1,-1), LIGHT),
        ("TOPPADDING",   (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0), (-1,-1), 6),
        ("LEFTPADDING",  (0,0), (-1,-1), 8),
    ]))
    story.append(ctbl)

    # ── ФУТЕР ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    story.append(gold_line())
    story.append(Paragraph(
        "КП действительно 30 дней · Integra Develop © 2026",
        S_FOOTER
    ))

    doc.build(story)
    print(f"PDF создан: {OUT}")

if __name__ == "__main__":
    build()
