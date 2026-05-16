#!/usr/bin/env python3
"""Generate admin guide PDF."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT

GOLD = HexColor('#C9A84C')
GOLD_LIGHT = HexColor('#E8C97A')
DARK = HexColor('#111111')
CARD = HexColor('#1a1a1a')
TEXT = HexColor('#c8c0b0')
WHITE = HexColor('#FAFAFA')
DIM = HexColor('#888888')


def build_pdf(output_path='admin_guide.pdf'):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2.5*cm,
        rightMargin=2.5*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()

    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    title_style = S('Title', fontSize=28, textColor=GOLD,
                    alignment=TA_CENTER, fontName='Helvetica-Bold',
                    spaceAfter=4)
    subtitle_style = S('Sub', fontSize=11, textColor=DIM,
                       alignment=TA_CENTER, fontName='Helvetica',
                       spaceAfter=20)
    h1_style = S('H1', fontSize=16, textColor=GOLD,
                 fontName='Helvetica-Bold', spaceBefore=18, spaceAfter=6)
    h2_style = S('H2', fontSize=12, textColor=WHITE,
                 fontName='Helvetica-Bold', spaceBefore=12, spaceAfter=4)
    body_style = S('Body', fontSize=10, textColor=TEXT,
                   fontName='Helvetica', leading=16, spaceAfter=6)
    note_style = S('Note', fontSize=9, textColor=DIM,
                   fontName='Helvetica-Oblique', leading=14, spaceAfter=4,
                   leftIndent=12)
    code_style = S('Code', fontSize=10, textColor=GOLD_LIGHT,
                   fontName='Courier-Bold', backColor=CARD,
                   borderPadding=(6, 8, 6, 8), leading=16)
    warn_style = S('Warn', fontSize=10, textColor=HexColor('#e74c3c'),
                   fontName='Helvetica-Bold', spaceAfter=6)

    story = []

    # Cover
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph('PLACE FOR BEAUTY', title_style))
    story.append(Paragraph('Руководство администратора сайта', subtitle_style))
    story.append(HRFlowable(width='100%', color=GOLD, thickness=0.5, spaceAfter=30))
    story.append(Paragraph(
        'Этот документ описывает, как управлять прайс-листом салона красоты '
        'через встроенную панель администратора.',
        body_style
    ))
    story.append(Spacer(1, 0.5*cm))

    # TOC-like
    toc_data = [
        ['1.', 'Вход в админку'],
        ['2.', 'Интерфейс панели'],
        ['3.', 'Управление услугами'],
        ['4.', 'Управление категориями'],
        ['5.', 'Изменение пароля'],
        ['6.', 'Частые вопросы'],
    ]
    toc_table = Table(toc_data, colWidths=[1*cm, 12*cm])
    toc_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0,0), (-1,-1), TEXT),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (0,-1), GOLD),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [CARD, DARK]),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
    ]))
    story.append(toc_table)
    story.append(Spacer(1, 1*cm))

    # --- Section 1 ---
    story.append(HRFlowable(width='100%', color=GOLD, thickness=0.3, spaceAfter=8))
    story.append(Paragraph('1. Вход в панель администратора', h1_style))
    story.append(Paragraph(
        'Административная панель доступна по адресу:', body_style))
    story.append(Paragraph('http://193.164.150.235/admin.html', code_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph('Данные для входа по умолчанию:', h2_style))

    creds_data = [
        ['Поле', 'Значение'],
        ['Логин', 'admin'],
        ['Пароль', 'beauty2024'],
    ]
    creds_table = Table(creds_data, colWidths=[5*cm, 8*cm])
    creds_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), GOLD),
        ('TEXTCOLOR', (0,0), (-1,0), black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,1), (-1,-1), TEXT),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [CARD, DARK]),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.3, HexColor('#333333')),
    ]))
    story.append(creds_table)
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        '⚠ Смените пароль после первого входа! (см. раздел 5)', warn_style))

    # --- Section 2 ---
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width='100%', color=GOLD, thickness=0.3, spaceAfter=8))
    story.append(Paragraph('2. Интерфейс панели', h1_style))
    story.append(Paragraph(
        'После входа вы увидите два раздела в боковом меню:', body_style))

    iface_data = [
        ['Раздел', 'Описание'],
        ['✂️  Услуги', 'Список всех услуг с ценами. Здесь вы можете добавить, изменить или удалить конкретную услугу.'],
        ['📂  Категории', 'Разделы прайс-листа (Стрижка, Маникюр и т.д.). Можно добавить новую категорию или переименовать существующую.'],
    ]
    iface_table = Table(iface_data, colWidths=[4*cm, 9.5*cm])
    iface_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), GOLD),
        ('TEXTCOLOR', (0,0), (-1,0), black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9.5),
        ('TEXTCOLOR', (0,1), (-1,-1), TEXT),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [CARD, DARK]),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.3, HexColor('#333333')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(iface_table)

    # --- Section 3 ---
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width='100%', color=GOLD, thickness=0.3, spaceAfter=8))
    story.append(Paragraph('3. Управление услугами', h1_style))

    actions = [
        ('Добавить новую услугу',
         '1. Перейдите в раздел «Услуги».\n'
         '2. Нажмите кнопку «+ Добавить» в правом верхнем углу.\n'
         '3. Выберите категорию из выпадающего списка.\n'
         '4. Введите название услуги и цену.\n'
         '5. Если цена приблизительная (например «от 5000»), заполните поле «Префикс» значением «от ».\n'
         '6. Нажмите «Сохранить».'),
        ('Редактировать услугу',
         '1. Найдите нужную услугу в списке (используйте фильтр по категории или поиск).\n'
         '2. Нажмите иконку карандаша ✎ справа от услуги.\n'
         '3. Измените нужные поля и нажмите «Сохранить».'),
        ('Скрыть услугу без удаления',
         '1. Откройте редактирование услуги.\n'
         '2. Снимите галочку «Активна».\n'
         '3. Нажмите «Сохранить». Услуга исчезнет с сайта, но останется в базе.'),
        ('Удалить услугу',
         '1. Нажмите иконку ✕ справа от услуги.\n'
         '2. Подтвердите удаление в диалоге.\n'
         '⚠ Удаление необратимо!'),
    ]

    for title, text in actions:
        story.append(Paragraph(title, h2_style))
        story.append(Paragraph(text.replace('\n', '<br/>'), note_style))
        story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph('Поля при добавлении/редактировании услуги:', h2_style))
    fields_data = [
        ['Поле', 'Обязательное', 'Пример'],
        ['Категория', 'Да', 'Женские стрижки'],
        ['Название', 'Да', 'Стрижка короткие'],
        ['Префикс цены', 'Нет', 'от'],
        ['Цена', 'Да', '1 500'],
        ['Описание', 'Нет', 'Включает мытьё головы'],
        ['Порядок', 'Нет', '5 (чем меньше — тем выше)'],
        ['Активна', 'Нет', 'Да/Нет'],
    ]
    ft = Table(fields_data, colWidths=[4.5*cm, 3*cm, 6*cm])
    ft.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), GOLD),
        ('TEXTCOLOR', (0,0), (-1,0), black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,1), (-1,-1), TEXT),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [CARD, DARK]),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('GRID', (0,0), (-1,-1), 0.3, HexColor('#333333')),
    ]))
    story.append(ft)

    # --- Section 4 ---
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width='100%', color=GOLD, thickness=0.3, spaceAfter=8))
    story.append(Paragraph('4. Управление категориями', h1_style))
    story.append(Paragraph(
        'Категории — это разделы прайс-листа. Клиенты видят их как вкладки на сайте.',
        body_style))

    cat_actions = [
        ('Добавить категорию',
         '1. Перейдите в раздел «Категории» в меню.\n'
         '2. Нажмите «+ Добавить».\n'
         '3. Введите название (обязательно), иконку (эмодзи) и порядок отображения.\n'
         '4. Slug (идентификатор) заполняется автоматически, но можно указать вручную.'),
        ('Переименовать категорию',
         '1. Найдите категорию в списке.\n'
         '2. Нажмите иконку ✎.\n'
         '3. Измените название или иконку и сохраните.'),
        ('Удалить категорию',
         '⚠ При удалении категории удаляются ВСЕ её услуги!\n'
         'Нажмите ✕ и подтвердите в диалоге.'),
    ]
    for title, text in cat_actions:
        story.append(Paragraph(title, h2_style))
        story.append(Paragraph(text.replace('\n', '<br/>'), note_style))
        story.append(Spacer(1, 0.2*cm))

    # --- Section 5 ---
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width='100%', color=GOLD, thickness=0.3, spaceAfter=8))
    story.append(Paragraph('5. Изменение пароля администратора', h1_style))
    story.append(Paragraph(
        'Пароль хранится в базе данных в зашифрованном виде. '
        'Чтобы изменить его, выполните следующие шаги на сервере:',
        body_style))
    story.append(Paragraph('ssh root@193.164.150.235', code_style))
    story.append(Paragraph('cd /opt/placeforbeauty', code_style))
    story.append(Paragraph('python3 change_password.py admin НОВЫЙ_ПАРОЛЬ', code_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        'Файл change_password.py уже находится в папке проекта на сервере.',
        note_style))

    # --- Section 6 ---
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width='100%', color=GOLD, thickness=0.3, spaceAfter=8))
    story.append(Paragraph('6. Частые вопросы', h1_style))

    faq = [
        ('Изменения на сайте видны сразу?',
         'Да. После сохранения изменений сайт обновляется мгновенно — '
         'перезагрузите страницу клиентского сайта.'),
        ('Можно ли восстановить удалённую услугу?',
         'Нет. Удаление необратимо. Рекомендуем скрывать услуги (снять галочку «Активна»), '
         'а не удалять их.'),
        ('Сайт не открывается — что делать?',
         'Проверьте, запущен ли сервис на VPS:\n'
         'ssh root@193.164.150.235\n'
         'systemctl status placeforbeauty'),
        ('Как перезапустить сайт?',
         'systemctl restart placeforbeauty'),
        ('Где хранится база данных?',
         '/opt/placeforbeauty/beauty.db — SQLite файл. '
         'Делайте резервные копии этого файла.'),
    ]

    for q, a in faq:
        story.append(KeepTogether([
            Paragraph(q, h2_style),
            Paragraph(a.replace('\n', '<br/>'), note_style),
            Spacer(1, 0.2*cm),
        ]))

    # Footer
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width='100%', color=GOLD, thickness=0.5, spaceAfter=12))
    story.append(Paragraph(
        'Place for Beauty © 2024 · Документ создан автоматически',
        S('Footer', fontSize=8, textColor=DIM, alignment=TA_CENTER, fontName='Helvetica')
    ))

    doc.build(story)
    print(f'PDF создан: {output_path}')


if __name__ == '__main__':
    build_pdf()
