# 	Challonge Discord Bot
# ----------------------------------------------------
# 	By Lucky "Luckstruck9" Lai
# 	www.luckstruck9.com
# ----------------------------------------------------
# 	Challonge PY Information
# 	https://pypi.org/project/pychal/
# 	https://api.challonge.com/v1
#
# 	Discord PY Information
# 	https://techwithtim.net/tutorials/discord-py/setup/
# ----------------------------------------------------
#   Install Commands:
#   pip install pychal
#   pip install discord
# ----------------------------------------------------

from datetime import datetime
import os
import sys
import discord
import time
import asyncio
import challonge

# Challonge Setup
challonge_username=""		# FILL IN
challonge_key=""			# FILL IN


try:
	client = discord.Client()								# Starts the Discord Client
	id = client.get_guild(DiscordServerID)					# Replace 'DiscordServerID' with your server ID			
	channel = client.get_channel(DiscordChannelID)			# Replace 'DiscordChannelID' with your channel ID
	print("SUCCESSFUL LOGIN!!!")
except:
	print("Errors loading Discord information")

# Data Storage Setup
printedmatches = []
matchlog=[]

def maxRounds(tournament):
	challonge.set_credentials(challonge_username,challonge_key)
	maxRound = [1, 1]
	for match in challonge.matches.index(tournament["id"]):
		if match["round"]>0:
			maxRound[0] = max(maxRound[0],match["round"])
		else:
			maxRound[1] = max(maxRound[1],abs(match["round"]))
	return maxRound

def roundnamefinder(maxRound, roundnum):
	name = ""
	if roundnum > 0:
		if roundnum == maxRound-1:
			name += "Finals"
		elif roundnum == maxRound-2:
			name += "Semis"
		elif roundnum == maxRound-3:
			name += "Qrts"
		else:
			name += "R"+str(abs(roundnum))
	else:
		if roundnum == maxRound:
			name += "Finals"
		elif roundnum == maxRound-1:
			name += "Semis"
		elif roundnum == maxRound-2:
			name += "Qrts"
		elif roundnum == maxRound-3:
			name += "Top 8"
		else:
			name += "R"+str(abs(roundnum))
	return name

def ChallongePrintLine():
	challonge.set_credentials(challonge_username,challonge_key)
	line = ""
	for tournament in (challonge.tournaments.index()):
		#print(tournament["created_at"].year)
		if (tournament["state"] == "underway"):
			sys.stdout.write("Sorting through tournament data..."+ tournament["name"]+"\n")
			for match in challonge.matches.index(tournament["id"]):
				if (match["state"] == "complete"):
					#sys.stdout.write("Potential Match Finished Message:"+str(match["round"])+"\n")

					player1 = str(challonge.participants.show(tournament["id"],match["player1_id"])["display_name_with_invitation_email_address"])
					player2 = str(challonge.participants.show(tournament["id"],match["player2_id"])["display_name_with_invitation_email_address"])
					scores = match["scores_csv"].split("-")
					roundname = match["round"]

					roundnamestr = ""
					if roundname == maxRounds(tournament)[0]:
						roundnamestr = "Grand Finals"
						if [player2, player1, roundname, False] in printedmatches:
							roundnamestr += "(2)"
					elif roundname > 0:
						roundnamestr += "Winners "
						roundnamestr += roundnamefinder(maxRounds(tournament)[0], roundname)
					else:
						roundnamestr += "Losers "
						roundnamestr += roundnamefinder(maxRounds(tournament)[1], roundname)


					checkdata = [player1, player2, roundname, True]
					if checkdata not in printedmatches:
						winmargin=""
						if scores[0]=="0" and scores[1]=="0":
							winmargin = "wins through forfeit against"
						else:
							winmargin = "wins against"

						if match["winner_id"] == match["player1_id"]:
							line+=str(tournament["name"]+"\t"+roundnamestr+"\t"+player1+" "+winmargin+" "+player2+"\t Score:"+str("-".join(scores))+"\n")
						elif match["winner_id"] == match["player2_id"]:
							line+=str(tournament["name"]+"\t"+roundnamestr+"\t"+player2+" "+winmargin+" "+player1+"\t Score:"+str("-".join(scores))+"\n")

						printedmatches.append(checkdata)
						print("Line added:",player1,"vs.",player2," is coming up. Players should prepare for their match to be called.", flush=True)

				if (match["state"] == "open"):
					#sys.stdout.write("Potential Match Pending Message \n")
					#print(str(challonge.participants.show(tournament["id"],match["player1_id"])))
					player1 = str(challonge.participants.show(tournament["id"],match["player1_id"])["display_name_with_invitation_email_address"])
					player2 = str(challonge.participants.show(tournament["id"],match["player2_id"])["display_name_with_invitation_email_address"])
					roundname = match["round"]
					checkdata = [player1, player2, roundname, False]
					
					roundnamestr = ""
					if roundname == maxRounds(tournament)[0]:
						roundnamestr = "Grand Finals"
						if [player2, player1, roundname, False] in printedmatches:
							roundnamestr += "(2)"
					elif roundname > 0:
						roundnamestr += "Winners "
						roundnamestr += roundnamefinder(maxRounds(tournament)[0], roundname)
					else:
						roundnamestr += "Losers "
						roundnamestr += roundnamefinder(maxRounds(tournament)[1], roundname)

					if checkdata not in printedmatches:
						line+=str(tournament["name"]+"\t"+roundnamestr+"\t"+player1+" vs. "+player2+" is coming up.\tPlayers should prepare for their match to be called. "+"\n")
						printedmatches.append(checkdata)
						print("Line added:",player1,"vs.",player2," is coming up. Players should prepare for their match to be called.", flush=True)
	return line

@client.event
async def on_ready():
	print("Bot Ready!")

async def update_stats():
	await client.wait_until_ready()
	channel = client.get_channel(DiscordChannelID)			# Replace 'DiscordChannelID' with your channel ID
	while not client.is_closed():
		try:
			challongeupdate = ChallongePrintLine()
			if challongeupdate != "":
				await channel.send(challongeupdate)
				print("Sending: \n",challongeupdate)
				matchlog.append(challongeupdate)
			await asyncio.sleep(5)

			os.system('clear')								# Use on Mac/Linux	
			os.system('cls')								# Use on Windows

			print('Logged in as')
			print(client.user.name)
			print(client.user.id)
			print("-----------------------")
			print("Match Log:")
			print("\n".join(matchlog))
			print("-----------------------")
			now = datetime.now()
			current_time = now.strftime("%H:%M:%S")
			sys.stdout.write("Checking for updates... Updated:"+current_time+"\n")
		except Exception as e:
			print(e)
			await asyncio.sleep(5)



client.loop.create_task(update_stats())
client.run(DiscordClientID)			# Replace 'DiscordClientID' with the client token from Discord Developer API
