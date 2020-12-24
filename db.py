from datetime import datetime


def transliterate(name):
    # Слоаврь с заменами
    dictionary = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'zh', 'з': 'z', 'и': 'i',
                  'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
                  'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'cz', 'ш': 'sh', 'щ': 'scz', 'ъ': '', 'ы': 'y', 'ь': '',
                  'э': 'e', 'ю': 'u', 'я': 'ja', ' ': '-'}
    # Циклически заменяем все буквы в строке
    for key in dictionary:
        name = name.lower().replace(key, dictionary[key])
    return name


def clear_bidding_lots_table(bidding_lots_table):
    for i in range(len(bidding_lots_table) - 1, -1, -1):
        if "tenderweek.com" not in str(bidding_lots_table[i][1]):
            del bidding_lots_table[i]
    return bidding_lots_table


def get_bidding_lots_table(con):
    cur = con.cursor()
    cur.execute("SELECT number, source_url FROM bidding_lots")
    bidding_lots_table = cur.fetchall()
    # print("bidding_lots_table =", len(bidding_lots_table))
    # bidding_lots_table_1 = clear_bidding_lots_table(bidding_lots_table)
    # print("bidding_lots_table_1 = ", len(bidding_lots_table_1))
    return bidding_lots_table


def in_table(lotNumber, lotLink, rows):
    # Проверяем на наличие лота в таблице
    # cur = con.cursor()
    # cur.execute("SELECT number, source_url FROM bidding_lots")
    # rows = cur.fetchall()
    for row in rows:
        if str(lotNumber) == str(row[0]) and str(lotLink) == str(row[1]):
            return True
    return False


def find_expired_lots(con):
    # находим просроченные лоты и изменяем их статус
    cur = con.cursor()
    # setting timezone for current session to avoid mistakes
    cur.execute("SET TIMEZONE=5")
    cur.execute("UPDATE bidding_lots SET status = 'expired', updated_at = now() WHERE ended_at < now()")
    con.commit()


def add_category(con, name):
    # добавить новую категорию в таблицу и вернуть новый id
    cur = con.cursor()
    cur.execute("SELECT id, slug FROM bidding_categories ORDER BY id")
    rows = cur.fetchall()
    for row in rows:
        if row[1] == transliterate(name):
            return row[0]
    category_id = rows[-1][0] + 1
    cur.execute(
        "INSERT INTO bidding_categories(id, parent_id, depth, path, slug, created_at, updated_at) VALUES (%s, %s, %s, "
        "%s, %s, now(), now())", (category_id, 41, 2, '/41/{}/'.format(rows[-1][0] + 1), transliterate(name)))
    con.commit()
    rows.clear()
    return category_id


def get_category_id(con, required):
    # вернуть id категории лота (если нет, то создать)
    if required.lower().replace(' ', '') == '':
        required = 'undefined'
    cur = con.cursor()
    cur.execute("SELECT category_id, name, id FROM bidding_categories_translations ORDER BY id")
    rows = cur.fetchall()
    for row in rows:
        if row[1].lower().replace(' ', '') == required.lower().replace(' ', ''):
            return row[0]
    print("Category was not found:", required)
    category_id = add_category(con, required)
    cur.execute("INSERT INTO bidding_categories_translations(id, category_id, name, locale) VALUES (%s, %s, %s, %s)",
                (rows[-1][2] + 1, category_id, required.lower().capitalize(), 'rus'))
    cur.execute("INSERT INTO bidding_categories_translations(id, category_id, name, locale) VALUES (%s, %s, %s, %s)",
                (rows[-1][2] + 2, category_id, required.lower().capitalize(), 'uzb'))
    con.commit()
    rows.clear()
    return category_id


def get_source_id(con, required):
    # вернуть id источника (если нет, то добавить заранее вручную)
    cur = con.cursor()
    cur.execute("SELECT id, url FROM bidding_sources ORDER BY id")
    rows = cur.fetchall()
    for row in rows:
        if row[1] in required:
            return row[0]
    print("Source was not found:", required)


def add_subject(con, name, lot):
    cur = con.cursor()
    cur.execute("SELECT id FROM bidding_subjects ORDER BY id")
    rows = cur.fetchall()
    new_id = rows[-1][0] + 1
    cur.execute(
        "INSERT INTO bidding_subjects(id, name, itin, address, phone, bank_account, website, image, created_at, "
        "updated_at, country_id, responsible_person, phone2, email) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, null, now(), now(), %s, null, %s, %s)", (
            new_id, name, lot.itin, lot.subject_address, lot.phone, lot.bank_account, lot.website, lot.country_id,
            lot.phone2, lot.email))
    con.commit()
    print("new id of subject", new_id)
    return new_id


def update_subject(con, row, lot):
    cur = con.cursor()
    lot_dict = lot.__dict__
    columns = ('id', 'name', 'itin', 'address', 'phone', 'bank_account', 'website', 'image', 'created_at', 'updated_at',
               'country_id', 'responsible_person, phone2', 'email2', 'email')
    new = dict(zip(columns, row))
    new.update(dict(update_at=datetime.now()))
    for i in new:
        if i in lot_dict and i != 'name':
            if lot_dict[i] is not None:
                new[i] = lot_dict[i]
                cur.execute(f"UPDATE bidding_subjects SET {i} = %s WHERE id=%s", (new[i], row[0]))
                con.commit()
    cur.execute("UPDATE bidding_subjects SET updated_at = %s WHERE id=%s", (new['updated_at'], row[0]))
    print("updated subject:", row[0])




def get_subject_id(con, required, lot):
    cur = con.cursor()
    cur.execute("SELECT id, name, itin, address, phone, bank_account, website, image, created_at, updated_at, "
                "country_id, responsible_person, phone2, email2, email FROM bidding_subjects ORDER BY id")
    rows = cur.fetchall()
    for row in rows:
        if row[1].lower().replace(' ', '') == required.lower().replace(' ', ''):
            update_subject(con, row, lot)
            return row[0]
    print("subject was not found:", required)
    subject_id = add_subject(con, required, lot)
    return subject_id


def get_country_id(con, required):
    # определить страну
    cur = con.cursor()
    cur.execute("SELECT country_id, name FROM geo_countries_translations")
    rows = cur.fetchall()
    for row in rows:
        if row[1] == required.capitalize():
            return row[0]
    print("Country was not found:", required)
    rows.clear()
    return -1


def get_region_id(con, required):
    # регионов узбекистана всего 15 (судя по таблице)
    # и добавление новых не в нашей юрисдикции
    # но если другая страна, нужно будет добавить функцию
    cur = con.cursor()
    cur.execute("SELECT region_id, name FROM geo_regions_translations")
    rows = cur.fetchall()
    if required == '' or required == '-' or required is None:
        required = 'Не указан'
    for row in rows:
        if row[1].lower().replace(' ', '') == required.replace('город', '').lower().replace(' ', ''):
            # print("get_region_id done successfully")
            return row[0]
    print("Region was not found:", required)
    rows.clear()
    return -1


def get_area_id(con, required):
    cur = con.cursor()
    cur.execute("SELECT area_id, name FROM geo_areas_translations")
    rows = cur.fetchall()
    scrap = required
    scrap = scrap.lower()
    scrap = scrap.replace(' ', '')
    scrap = scrap.replace('район', '')
    scrap = scrap.replace('р-он', '')
    scrap = scrap.replace('г.', '')
    scrap = scrap.replace('p', 'р')
    for row in rows:
        if scrap in row[1].lower().replace(' ', ''):
            return row[0]
    print("Area was not found:", required)
    rows.clear()
    return -1


def get_for_this_lot(con, currentLot):
    currentLot.category_id = get_category_id(con, currentLot.category)
    currentLot.source_id = get_source_id(con, currentLot.source_url)
    currentLot.subject_id = get_subject_id(con, currentLot.subject, currentLot)


def get_for_everything(con, listOfLots):  # название временное
    print("Processing data...")
    for lot in listOfLots:
        get_for_this_lot(con, lot)
    print("Data was processed successfully\n"
          "Adding to Database...")


def get_id_from_bidding_lots(con):
    cur = con.cursor()
    cur.execute("SELECT id FROM bidding_lots ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    return row[0] + 1


def save_lot_in_bidding_lots(con, lot):
    cur = con.cursor()
    new_id = get_id_from_bidding_lots(con)
    cur.execute("INSERT INTO bidding_lots(id, type, number, category_id, source_url, advance_amount, "
                "advance_payment_days, "
                "remains_payment_days, deposit_amount, started_at, ended_at, status, is_visible, is_approved, created_at, "
                "updated_at, subject_id, winner_id, source_id, country_id, region_id, area_id, price, currency_id, parent_id,"
                "closed_at, views, transaction_number, transaction_sum, price_lowest, participants, quantity) "
                "VALUES (%s, %s, %s, %s, %s, null, null, null, null, %s, %s, %s, true, true, now(), now(), %s, null, "
                "%s, %s, "
                "%s, %s, null, null, null, null, 0, null, null, null, null, null)", (
                    new_id, lot.type, lot.number, lot.category_id, lot.source_url, lot.started_at, lot.ended_at,
                    lot.status, lot.subject_id, lot.source_id, lot.country_id, lot.region_id, lot.area_id))
    con.commit()
    return new_id


def get_id_from_bidding_lots_translations(con):
    cur = con.cursor()
    cur.execute("SELECT id FROM bidding_lots_translations ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    return row[0] + 1


def save_lot_in_bidding_lots_translations(con, lot):
    lot_id = save_lot_in_bidding_lots(con, lot)
    new_id = get_id_from_bidding_lots_translations(con)
    cur = con.cursor()
    cur.execute("INSERT INTO bidding_lots_translations(id, lot_id, name, description_short, description_long, "
                "purchase_conditions, delivery_conditions, delivery_time, locale, delivery_address, measure) "
                "VALUES (%s, %s, %s, %s, null, %s, %s, %s, %s, %s, null)", (
                    new_id, lot_id, lot.name, lot.description_short, lot.purchase_conditions, lot.delivery_conditions,
                    lot.delivery_time, 'rus', lot.delivery_address))
    cur.execute("INSERT INTO bidding_lots_translations(id, lot_id, name, description_short, description_long, "
                "purchase_conditions, delivery_conditions, delivery_time, locale, delivery_address, measure) "
                "VALUES (%s, %s, %s, %s, null, %s, %s, %s, %s, %s, null)", (
                    new_id + 1, lot_id, lot.name, lot.description_short, lot.purchase_conditions,
                    lot.delivery_conditions, lot.delivery_time, 'uzb', lot.delivery_address))

    print("id: {}; lot_id: {}".format(new_id, lot_id))
    con.commit()


def save_lot(con, lot):
    save_lot_in_bidding_lots_translations(con, lot)
