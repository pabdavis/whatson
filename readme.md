whatson bot

bot runs every 15 minutes from 4am to 11pm

checks a specific twitter list for users

RTs last status from each user, waiting 30 seconds between users

If RT was already sent, it doesn't RT

every time it runs, it adds its everything it RTs to a log

it runs again at 12pm, sending an email reporting on its progress

it then clears the log so it can start again