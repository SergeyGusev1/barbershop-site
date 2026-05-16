#!/usr/bin/env python3
"""Generate admin guide PDF."""
import os, sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT

GOLD       = HexColor('#C9A84C')
GOLD_LIGHT = HexColor('#E8C97A')
DARK       = HexColor('#111111')
CARD       = HexColor('#1a1a1a')
TEXT       = HexColor('#c8c0b0')
WHITE      = HexColor('#FAFAFA')
DIM        = HexColor('#888888')


# ── Шрифты с поддержкой кириллицы ───────────────────────────────────────────
_FONT_CANDIDATES = [
    # Linux (DejaVu — обычно предустановлен)
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    # Linux alternative
    ("/usr/share/fonts/dejavu/DejaVuSans.ttf",
     "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"),
    # Windows
    ("C:/Windows/Fonts/arial.ttf",   "C:/Windows/Fonts/arialbd.ttf"),
    ("C:/Windows/Fonts/calibri.ttf", "C:/Windows/Fonts/calibrib.ttf"),
    # macOS
    ("/Library/Fonts/Arial.ttf",     "/Library/Fonts/Arial Bold.ttf"),
    ("/System/Library/Fonts/Supplemental/Arial.ttf",
     "/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
]

def _register_fonts():
    for reg, bold in _FONT_CANDIDATES:
        if os.path.exists(reg):
            try:
                pdfmetrics.registerFont(TTFont("CyrFont",     reg))
                if os.path.exists(bold):
                    pdfmetrics.registerFont(TTFont("CyrFont-Bold", bold))
                else:
                    pdfmetrics.registerFont(TTFont("CyrFont-Bold", reg))
                return "CyrFont", "CyrFont-Bold"
            except Exception:
                continue
    # Крайний случай — шрифт не найден, кириллица не отобразится
    print("WARNING: No Cyrillic font found, using Helvetica (Cyrillic may not render)")
    return "Helvetica", "Helvetica-Bold"

FONT, FONT_BOLD = _register_fonts()


def build_pdf(output_path='admin_guide.pdf'):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2.5*cm, rightMargin=2.5*cm,
        topMargin=2*cm,    bottomMargin=2*cm,
    )

    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    title_style    = S('Title',    fontSize=28, textColor=GOLD,
                       alignment=TA_CENTER, fontName=FONT_BOLD, spaceAfter=4)
    subtitle_style = S('Sub',      fontSize=11, textColor=DIM,
                       alignment=TA_CENTER, fontName=FONT,      spaceAfter=20)
    h1_style       = S('H1',       fontSize=16, textColor=GOLD,
                       fontName=FONT_BOLD, spaceBefore=18, spaceAfter=6)
    h2_style       = S('H2',       fontSize=12, textColor=WHITE,
                       fontName=FONT_BOLD, spaceBefore=12, spaceAfter=4)
    body_style     = S('Body',     fontSize=10, textColor=TEXT,
                       fontName=FONT, leading=16, spaceAfter=6)
    note_style     = S('Note',     fontSize=9,  textColor=DIM,
                       fontName=FONT, leading=14, spaceAfter=4, leftIndent=12)
    code_style     = S('Code',     fontSize=10, textColor=GOLD_LIGHT,
                       fontName='Courier-Bold', backColor=CARD,
                       borderPadding=(6, 8, 6, 8), leading=16)
    warn_style     = S('Warn',     fontSize=10, textColor=HexColor('#e74c3c'),
                       fontName=FONT_BOLD, spaceAfter=6)
    footer_style   = S('Footer',   fontSize=8,  textColor=DIM,
                       alignment=TA_CENTER, fontName=FONT)

    def gold_hr():
        return HRFlowable(width='100%', color=GOLD, thickness=0.3, spaceAfter=8)

    def tbl_style_base():
        return [
            ('LEFTPADDING',  (0,0), (-1,-1), 8),
            ('TOPPADDING',   (0,0), (-1,-1), 7),
            ('BOTTOMPADDING',(0,0), (-1,-1), 7),
        ]

    story = []

    # ── Обложка ─────────────────────────────────────────────────────────────
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph('PLACE FOR BEAUTY', title_style))
    story.append(Paragraph('Руководство администратора сайта', subtitle_style))
    story.append(HRFlowable(width='100%', color=GOLD, thickness=0.5, spaceAfter=30))
    story.append(Paragraph(
        'Этот документ описывает, как управлять прайс-листом салона красоты '
        'через встроенную панель администратора.',
        body_style))
    story.append(Spacer(1, 0.5*cm))

    # ── Содержание ──────────────────────────────────────────────────────────
    toc_data = [
        ['1.', 'Вход в админку'],
        ['2.', 'Интерфейс панели'],
        ['3.', 'Управление услугами'],
        ['4.', 'Управление категориями'],
        ['5.', 'Изменение пароля'],
        ['6.', 'Частые вопросы'],
    ]
    toc = Table(toc_data, colWidths=[1*cm, 12*cm])
    toc.setStyle(TableStyle([
        ('TEXTCOLOR',      (0,0), (-1,-1), TEXT),
        ('FONTNAME',       (0,0), (-1,-1), FONT),
        ('FONTSIZE',       (0,0), (-1,-1), 10),
        ('TEXTCOLOR',      (0,0), (0,-1),  GOLD),
        ('FONTNAME',       (0,0), (0,-1),  FONT_BOLD),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [CARD, DARK]),
        ('LEFTPADDING',    (0,0), (-1,-1), 10),
        ('TOPPADDING',     (0,0), (-1,-1), 7),
        ('BOTTOMPADDING',  (0,0), (-1,-1), 7),
    ]))
    story.append(toc)
    story.append(Spacer(1, 1*cm))

    # ── Раздел 1 — Вход ─────────────────────────────────────────────────────
    story.append(gold_hr())
    story.append(Paragraph('1. Вход в панель администратора', h1_style))
    story.append(Paragraph('Административная панель доступна по адресу:', body_style))
    story.append(Paragraph('http://193.164.150.235/admin.html', code_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph('Данные для входа по умолчанию:', h2_style))

    creds = Table(
        [['Поле', 'Значение'], ['Логин', 'admin'], ['Пароль', 'beauty2024']],
        colWidths=[5*cm, 8*cm]
    )
    creds.setStyle(TableStyle([
        ('BACKGROUND',     (0,0), (-1,0),  GOLD),
        ('TEXTCOLOR',      (0,0), (-1,0),  black),
        ('FONTNAME',       (0,0), (-1,0),  FONT_BOLD),
        ('FONTSIZE',       (0,0), (-1,-1), 10),
        ('TEXTCOLOR',      (0,1), (-1,-1), TEXT),
        ('FONTNAME',       (0,1), (-1,-1), FONT),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [CARD, DARK]),
        ('LEFTPADDING',    (0,0), (-1,-1), 10),
        ('TOPPADDING',     (0,0), (-1,-1), 8),
        ('BOTTOMPADDING',  (0,0), (-1,-1), 8),
        ('GRID',           (0,0), (-1,-1), 0.3, HexColor('#333333')),
    ]))
    story.append(creds)
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        'ВНИМАНИЕ: Смените пароль после первого входа! (см. раздел 5)', warn_style))

    # ── Раздел 2 — Интерфейс ────────────────────────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    story.append(gold_hr())
    story.append(Paragraph('2. Интерфейс панели', h1_style))
    story.append(Paragraph(
        'После входа вы увидите два раздела в боковом меню:', body_style))

    iface = Table([
        ['Раздел', 'Описание'],
        ['Услуги',
         'Список всех услуг с ценами. Здесь можно добавить, изменить или удалить конкретную услугу.'],
        ['Категории',
         'Разделы прайс-листа (Стрижка, Маникюр и т.д.). '
         'Можно добавить новую категорию или переименовать существующую.'],
    ], colWidths=[4*cm, 9.5*cm])
    iface.setStyle(TableStyle([
        ('BACKGROUND',     (0,0), (-1,0),  GOLD),
        ('TEXTCOLOR',      (0,0), (-1,0),  black),
        ('FONTNAME',       (0,0), (-1,0),  FONT_BOLD),
        ('FONTSIZE',       (0,0), (-1,-1), 9.5),
        ('TEXTCOLOR',      (0,1), (-1,-1), TEXT),
        ('FONTNAME',       (0,1), (-1,-1), FONT),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [CARD, DARK]),
        ('LEFTPADDING',    (0,0), (-1,-1), 10),
        ('TOPPADDING',     (0,0), (-1,-1), 10),
        ('BOTTOMPADDING',  (0,0), (-1,-1), 10),
        ('GRID',           (0,0), (-1,-1), 0.3, HexColor('#333333')),
        ('VALIGN',         (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(iface)

    # ── Раздел 3 — Услуги ───────────────────────────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    story.append(gold_hr())
    story.append(Paragraph('3. Управление услугами', h1_style))

    for title, text in [
        ('Добавить новую услугу',
         '1. Перейдите в раздел «Услуги».<br/>'
         '2. Нажмите кнопку «+ Добавить» в правом верхнем углу.<br/>'
         '3. Выберите категорию из выпадающего списка.<br/>'
         '4. Введите название услуги и цену.<br/>'
         '5. Если цена приблизительная — заполните поле «Префикс» значением «от ».<br/>'
         '6. Нажмите «Сохранить».'),
        ('Редактировать услугу',
         '1. Найдите нужную услугу (используйте фильтр по категории или поиск).<br/>'
         '2. Нажмите иконку карандаша справа от услуги.<br/>'
         '3. Измените нужные поля и нажмите «Сохранить».'),
        ('Скрыть услугу без удаления',
         '1. Откройте редактирование услуги.<br/>'
         '2. Снимите галочку «Активна».<br/>'
         '3. Нажмите «Сохранить» — услуга исчезнет с сайта, но останется в базе.'),
        ('Удалить услугу',
         '1. Нажмите иконку удаления справа от услуги.<br/>'
         '2. Подтвердите удаление в диалоге.<br/>'
         'ВНИМАНИЕ: Удаление необратимо!'),
    ]:
        story.append(Paragraph(title, h2_style))
        story.append(Paragraph(text, note_style))
        story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph('Поля при добавлении/редактировании услуги:', h2_style))
    ft = Table([
        ['Поле',        'Обязательное', 'Пример'],
        ['Категория',   'Да',           'Женские стрижки'],
        ['Название',    'Да',           'Стрижка короткие'],
        ['Префикс',     'Нет',          'от'],
        ['Цена',        'Да',           '1 500'],
        ['Описание',    'Нет',          'Включает мытьё головы'],
        ['Порядок',     'Нет',          '5 (чем меньше — тем выше)'],
        ['Активна',     'Нет',          'Да / Нет'],
    ], colWidths=[4.5*cm, 3*cm, 6*cm])
    ft.setStyle(TableStyle([
        ('BACKGROUND',     (0,0), (-1,0),  GOLD),
        ('TEXTCOLOR',      (0,0), (-1,0),  black),
        ('FONTNAME',       (0,0), (-1,0),  FONT_BOLD),
        ('FONTSIZE',       (0,0), (-1,-1), 9),
        ('TEXTCOLOR',      (0,1), (-1,-1), TEXT),
        ('FONTNAME',       (0,1), (-1,-1), FONT),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [CARD, DARK]),
        ('LEFTPADDING',    (0,0), (-1,-1), 8),
        ('TOPPADDING',     (0,0), (-1,-1), 7),
        ('BOTTOMPADDING',  (0,0), (-1,-1), 7),
        ('GRID',           (0,0), (-1,-1), 0.3, HexColor('#333333')),
    ]))
    story.append(ft)

    # ── Раздел 4 — Категории ────────────────────────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    story.append(gold_hr())
    story.append(Paragraph('4. Управление категориями', h1_style))
    story.append(Paragraph(
        'Категории — это разделы прайс-листа. Клиенты видят их как вкладки на сайте.',
        body_style))

    for title, text in [
        ('Добавить категорию',
         '1. Перейдите в раздел «Категории» в меню.<br/>'
         '2. Нажмите «+ Добавить».<br/>'
         '3. Введите название (обязательно), иконку и порядок отображения.<br/>'
         '4. Slug заполняется автоматически, но можно указать вручную.'),
        ('Переименовать категорию',
         '1. Найдите категорию в списке.<br/>'
         '2. Нажмите иконку редактирования.<br/>'
         '3. Измените название или иконку и сохраните.'),
        ('Удалить категорию',
         'ВНИМАНИЕ: При удалении категории удаляются ВСЕ её услуги!<br/>'
         'Нажмите кнопку удаления и подтвердите в диалоге.'),
    ]:
        story.append(Paragraph(title, h2_style))
        story.append(Paragraph(text, note_style))
        story.append(Spacer(1, 0.2*cm))

    # ── Раздел 5 — Пароль ───────────────────────────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    story.append(gold_hr())
    story.append(Paragraph('5. Изменение пароля администратора', h1_style))
    story.append(Paragraph(
        'Пароль хранится в зашифрованном виде. '
        'Для смены выполните на сервере:', body_style))
    story.append(Paragraph('ssh root@193.164.150.235', code_style))
    story.append(Paragraph('cd /opt/placeforbeauty', code_style))
    story.append(Paragraph('python3 change_password.py admin НОВЫЙ_ПАРОЛЬ', code_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        'Файл change_password.py уже находится в папке проекта на сервере.',
        note_style))

    # ── Раздел 6 — FAQ ──────────────────────────────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    story.append(gold_hr())
    story.append(Paragraph('6. Частые вопросы', h1_style))

    for q, a in [
        ('Изменения на сайте видны сразу?',
         'Да. После сохранения сайт обновляется мгновенно — '
         'перезагрузите страницу клиентского сайта.'),
        ('Можно ли восстановить удалённую услугу?',
         'Нет, удаление необратимо. Рекомендуем скрывать услуги '
         '(снять галочку «Активна»), а не удалять их.'),
        ('Сайт не открывается — что делать?',
         'Проверьте сервис на VPS:<br/>'
         'ssh root@193.164.150.235<br/>'
         'systemctl status placeforbeauty'),
        ('Как перезапустить сайт?',
         'systemctl restart placeforbeauty'),
        ('Где хранится база данных?',
         '/opt/placeforbeauty/beauty.db — SQLite-файл. '
         'Делайте резервные копии этого файла.'),
    ]:
        story.append(KeepTogether([
            Paragraph(q, h2_style),
            Paragraph(a, note_style),
            Spacer(1, 0.2*cm),
        ]))

    # ── Футер ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width='100%', color=GOLD, thickness=0.5, spaceAfter=12))
    story.append(Paragraph(
        'Place for Beauty — Руководство администратора · Integra Develop 2026',
        footer_style))

    doc.build(story)
    print(f'PDF создан: {output_path}')


if __name__ == '__main__':
    build_pdf()
