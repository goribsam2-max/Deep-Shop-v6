import re

with open("pages/Profile.tsx", "r") as f:
    content = f.read()

# Update "To Pay"
content = content.replace('o.status === OrderStatus.PENDING', '(o.status === OrderStatus.PENDING || o.status === OrderStatus.CHECKING_PAYMENT)')

# Update "To Ship" -> APPROVED, PROCESSING, PACKAGING, COMPLETE_PACKAGING
old_ship = 'o.status === OrderStatus.SHIPPED || o.status === OrderStatus.ON_THE_WAY'
new_ship = '[OrderStatus.APPROVED, OrderStatus.PROCESSING, OrderStatus.PACKAGING, OrderStatus.COMPLETE_PACKAGING].includes(o.status)'
content = content.replace(old_ship, new_ship)

# Update "To Receive" -> SHIPPED, DELIVER_ON_COURIER, ON_THE_WAY
old_receive = 'o.status === OrderStatus.DELIVERED && (Date.now() - ((o as any).updatedAt || o.createdAt)) <= 24 * 60 * 60 * 1000'
new_receive = '[OrderStatus.SHIPPED, OrderStatus.DELIVER_ON_COURIER, OrderStatus.ON_THE_WAY].includes(o.status)'
content = content.replace(old_receive, new_receive)

with open("pages/Profile.tsx", "w") as f:
    f.write(content)

