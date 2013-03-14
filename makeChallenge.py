import synapseclient
import synapseHelpers
syn = synapseclient.Synapse()
syn.login()

##Create a new competition
#comp, leaderboard = synapseHelpers.createEvaluationBoard(name='GBM survival Prediction', 
#                                                         parentId='syn537704', 
#                                                         status='OPEN')
#print comp['id'], '\n\n', #leaderboard
#syn.onweb(leaderboard)
#syn.addEvaluationParticipant(comp)
comp='1709745'
leaderboard='syn1709746'



######################################
#Make a submission to an evaluation
######################################
#subEntity = syn.getEntity('syn1680964')
#syn.submitForEvaluation(comp, 'syn1680964')

##Make multiple submissions from Chris Bare
#ids= syn.query('select id from entity where parentId=="syn1701291"')
#for id in ids['results'][:10]:
#    syn.submitForEvaluation(comp, id['entity.id'])
#Remove a submission from the evaluation
#syn.removeForEvaluation('1709747')

#Modify score of submissions
for submission in  syn.getEvaluationSubmissions(evaluation):
    status =  syn.getEvaluationSubmissionStatus(submission)
    print status

#synapseHelpers.updateLeaderboard(leaderboard, comp)



#Clean up and remove all of the evaluations and leaderboard location
#syn.deleteEvaluation(comp)
#syn.deleteEntity(leaderboard)
