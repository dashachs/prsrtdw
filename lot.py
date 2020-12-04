from datetime import datetime


class Lot:
    def __init__(self, name=None, description_short=None, description_long=None, parent_id=None, parent=None,
                 country=None, country_id=220, region=None, region_id=10, area=None, area_id=125, subject=None,
                 subject_id=None, category=None, category_id=None, source_id=None, currency=None, currency_id=None,
                 winner=None, winner_id=None, type=None, number=None, source_url=None, quantity=None, measure=None,
                 price=None, price_lowest=None, participants=None, advance_amount=None, advance_payment_days=None,
                 remains_payment_days=None, deposit_amount=None, payment_term=None, started_at=None, closed_at=None,
                 ended_at=None, status='relevant', is_visible=None, is_approved=None, purchase_conditions=None,
                 delivery_address=None, delivery_conditions=None, delivery_time=None, delivery_term=None,
                 transaction_number=None, transaction_sum=None, created_at=datetime.now(), updated_at=datetime.now(),
                 email=None, email2=None, phone=None, phone2=None, is_sublot=False, attached_file=None,
                 subject_address=None, itin=None, bank_account=None):
        self.name = name  # название / purchase name
        self.description_short = description_short
        self.description_long = description_long
        self.parent_id = parent_id
        self.parent = parent
        self.country = country
        self.country_id = country_id
        self.region = region
        self.region_id = region_id
        self.area = area
        self.area_id = area_id
        self.subject = subject
        self.subject_id = subject_id
        self.category = category
        self.category_id = category_id
        self.source_id = source_id
        self.currency = currency
        self.currency_id = currency_id
        self.winner = winner
        self.winner_id = winner_id
        self.type = type
        self.number = number  # номер лота (lot id)
        self.source_url = source_url
        self.quantity = quantity
        self.measure = measure
        self.price = price
        self.price_lowest = price_lowest
        self.participants = participants
        self.advance_amount = advance_amount
        self.advance_payment_days = advance_payment_days
        self.remains_payment_days = remains_payment_days
        self.deposit_amount = deposit_amount
        self.payment_term = payment_term
        self.started_at = started_at
        self.closed_at = closed_at
        self.ended_at = ended_at
        self.status = status
        self.is_visible = is_visible
        self.is_approved = is_approved
        self.purchase_conditions = purchase_conditions
        self.delivery_address = delivery_address
        self.delivery_conditions = delivery_conditions
        self.delivery_time = delivery_time
        self.delivery_term = delivery_term
        self.transaction_number = transaction_number
        self.transaction_sum = transaction_sum
        self.created_at = created_at
        self.updated_at = updated_at
        self.email = email  # email компании
        self.email2 = email2  # email ответственного лица
        self.phone = phone
        self.phone2 = phone2
        self.is_sublot = is_sublot
        self.attached_file = attached_file
        self.subject_address = subject_address
        self.itin = itin
        self.bank_account = bank_account
