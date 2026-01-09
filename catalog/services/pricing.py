# catalog/services/pricing.py

def net_proceeds(price: float, tax_rate=7.5, shipping=6.72, ebay_comm=15.3, xaction_fee=0.30) -> float:
    ebay_comm = ebay_comm / 100
    tax_rate = tax_rate / 100
    return price - (((price * (1 + tax_rate)) + shipping) * ebay_comm) - xaction_fee


def listing_price(target_net: float, tax_rate=7.5, shipping=6.72, ebay_comm=15.3, xaction_fee=0.30) -> float:
    ebay_comm = ebay_comm / 100
    tax_rate = tax_rate / 100
    denom = 1 - (1 + tax_rate) * ebay_comm
    if denom <= 0:
        raise ValueError("Invalid rates: (1 + tax_rate) * ebay_comm must be < 1.")
    return (target_net + (shipping * ebay_comm) + xaction_fee) / denom
