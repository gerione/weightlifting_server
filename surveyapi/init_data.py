


db.session.add(Weightclass(name="W-48", min_weight=0, max_weight=48, sex=True))
db.session.add(Weightclass(name="W-53", min_weight=48, max_weight=53, sex=True))
db.session.add(Weightclass(name="W-58", min_weight=53, max_weight=58, sex=True))
db.session.add(Weightclass(name="W-63", min_weight=58, max_weight=63, sex=True))
db.session.add(Weightclass(name="W-69", min_weight=63, max_weight=69, sex=True))
db.session.add(Weightclass(name="W-75", min_weight=69, max_weight=75, sex=True))
db.session.add(Weightclass(name="W-90", min_weight=75, max_weight=90, sex=True))
db.session.add(Weightclass(name="W+90", min_weight=90, max_weight=9999, sex=True))

db.session.add(Weightclass(name="M-56", min_weight=0, max_weight=56, sex=False))
db.session.add(Weightclass(name="M-62", min_weight=56, max_weight=62, sex=False))
db.session.add(Weightclass(name="M-69", min_weight=62, max_weight=69, sex=False))
db.session.add(Weightclass(name="M-77", min_weight=69, max_weight=77, sex=False))
db.session.add(Weightclass(name="M-85", min_weight=77, max_weight=85, sex=False))
db.session.add(Weightclass(name="M-94", min_weight=85, max_weight=94, sex=False))
db.session.add(Weightclass(name="M-105", min_weight=94, max_weight=105, sex=False))
db.session.add(Weightclass(name="M+105", min_weight=105, max_weight=9999, sex=False))

