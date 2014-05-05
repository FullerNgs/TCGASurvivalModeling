import synapseclient
import synapseHelpers
syn = synapseclient.Synapse()
syn.login()

##Create a new competition
evaluation = syn.store(synapseclient.Evaluation(name='Pancancer Survival Prediction', 
                                                status='OPEN', contentSource='syn1710282'))
print 'Evaluation:', evaluation.id   #Evaluation: 1876290
syn.addEvaluationParticipant(evaluation)  #Add myself to the evaluation
homeEntity=syn.get('syn1710282')


##Create wiki page for competition
homeWikiPage = synapseclient.Wiki(title="TCGA Pancancer Survival Prediction", 
                                  markdown=open('description.md').read(),
                                  owner=homeEntity)
homeWikiPage = syn.store(homeWikiPage)
print 'Home wiki:', homeWikiPage.id  #Home wiki: 27303


#Create sub wiki page containing leaderboard
lbWiki = synapseclient.Wiki(title="Leaderboard", owner=evaluation, parentWikiId=homeWikiPage.id)
lbWiki = syn.store(lbWiki)
print 'Leaderboard:', lbWiki.id  #Leaderboard: 55678


