DUNGEONS = {"Shatters": {"reacts": [708243809229602827, 708243794797133875, 708243761695686746, 708243722562961488,
                                    708243745488896001, 708243777856208936],
                         "embed": ["Shatters", 708243809229602827, 708243794797133875,
                                   [708243761695686746, 708243722562961488,
                                    708243745488896001, 708243777856208936]]},
            "Parasite": {"reacts": [708430610502254653, 708430634410049669, 708243761695686746, 708243722562961488,
                                    708243745488896001, 708243777856208936],
                         "embed": ["Parasite Chambers", 708430610502254653, 708430634410049669,
                                   [708243761695686746, 708243722562961488,
                                    708243745488896001, 708243777856208936]]},
            "Lab": {"reacts": [709126276404740136, 709126308835360768, 708243777856208936],
                    "embed": ["Mad Lab", 709126276404740136, 709126308835360768, [708243777856208936]]}}


class AFKCheck:
    def __init__(self, chl, msg, rl, dun, loc):
        self.channel = chl
        self.message_id = msg
        self.leader = rl
        self.dungeon = dun
        self.key = None
        self.key_reacts = []
        self.location = loc
        self.status = 0
        self.raiders = []

    def __str__(self):
        return "AFK Check started in Channel ID {}, message ID {} by <@{}>.".format(self.channel, self.message_id,
                                                                                    self.leader)


class Raider:
    def __init__(self, disc, ign):
        self.discord_id = disc
        self.ign = ign
        self.runs_completed = 0
        self.runs_led = 0
        self.verified = True
        self.is_rl = False
        self.keys_opened = 0

    def __str__(self):
        return "{}, ID {}, c/l/k {}, {}, {}".format(self.ign, self.discord_id, self.runs_completed, self.runs_led,
                                                     self.keys_opened)
