colors = {
	"aquamarine": "#00FDB2",
	"mentorwings": "#FF6600",
	"s2logo": "#FF0000",
	"sgm": "#DD0040",
	"gmgold": "#DD0040",
	"gmshield": "#DD0040",
	"banhammer": "#DD0040",
	"tech": "#DD0040",
	"sbteye": "#0059FF",
	"emerald": "#1CFC2F",
	"stardustgreen": "#1CFC2F",
	"tanzanite": "#863EF0",
	"pink": "#FC65A5",
	"diamond": "#2ACC1FA",
	"goldshield": "#DBBF4A",
	"silvershield": "#7C8DA7",
	"frostfieldssilver": "#D3DDEB",
	"white": "#FFFFFF",
	"": "#FFFFFF"
}

def normalize_nick(nick):
	nick = nick.lower()
	if nick[0] == '[':
		return nick[nick.index(']') + 1 :]
	else:
		return nick
def user_upgrades(info, offset=0):
	id = info[2]
	retval = {
		"color": info[5+offset] in colors and colors[info[5+offset]] or '',
		"symbol": len(info[4+offset]) > 0 and info[4+offset] or "default"
	}
	return retval
