#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import *
from modeles import modeleResanet
from technique import datesResanet


app = Flask( __name__ )
app.secret_key = 'resanet'


@app.route( '/' , methods = [ 'GET' ] )
def index() :
	return render_template( 'vueAccueil.html' )

@app.route( '/usager/session/choisir' , methods = [ 'GET' ] )
def choisirSessionUsager() :
	return render_template( 'vueConnexionUsager.html' , carteBloquee = False , echecConnexion = False , saisieIncomplete = False )

@app.route( '/usager/seConnecter' , methods = [ 'POST' ] )
def seConnecterUsager() :
	numeroCarte = request.form[ 'numeroCarte' ]
	mdp = request.form[ 'mdp' ]

	if numeroCarte != '' and mdp != '' :
		usager = modeleResanet.seConnecterUsager( numeroCarte , mdp )
		if len(usager) != 0 :
			if usager[ 'activee' ] == True :
				session[ 'numeroCarte' ] = usager[ 'numeroCarte' ]
				session[ 'nom' ] = usager[ 'nom' ]
				session[ 'prenom' ] = usager[ 'prenom' ]
				session[ 'mdp' ] = mdp
				
				return redirect( '/usager/reservations/lister' )
				
			else :
				return render_template('vueConnexionUsager.html', carteBloquee = True , echecConnexion = False , saisieIncomplete = False )
		else :
			return render_template('vueConnexionUsager.html', carteBloquee = False , echecConnexion = True , saisieIncomplete = False )
	else :
		return render_template('vueConnexionUsager.html', carteBloquee = False , echecConnexion = False , saisieIncomplete = True)


@app.route( '/usager/seDeconnecter' , methods = [ 'GET' ] )
def seDeconnecterUsager() :
	session.pop( 'numeroCarte' , None )
	session.pop( 'nom' , None )
	session.pop( 'prenom' , None )
	return redirect( '/' )


@app.route( '/usager/reservations/lister' , methods = [ 'GET' ] )
def listerReservations() :
	tarifRepas = modeleResanet.getTarifRepas( session[ 'numeroCarte' ] )
	
	soldeCarte = modeleResanet.getSolde( session[ 'numeroCarte' ] )
	
	solde = '%.2f' % ( soldeCarte , )

	aujourdhui = datesResanet.getDateAujourdhuiISO()

	datesPeriodeISO = datesResanet.getDatesPeriodeCouranteISO()
	
	datesResas = modeleResanet.getReservationsCarte( session[ 'numeroCarte' ] , datesPeriodeISO[ 0 ] , datesPeriodeISO[ -1 ] )
	
	dates = []
	for uneDateISO in datesPeriodeISO :
		uneDate = {}
		uneDate[ 'iso' ] = uneDateISO
		uneDate[ 'fr' ] = datesResanet.convertirDateISOversFR( uneDateISO )


		if uneDateISO <= aujourdhui :
			uneDate[ 'verrouillee' ] = True
		else :
			uneDate[ 'verrouillee' ] = False

		if uneDateISO in datesResas :
			uneDate[ 'reservee' ] = True
		else :
			uneDate[ 'reservee' ] = False

		if soldeCarte < tarifRepas and uneDate[ 'reservee' ] == False :
			uneDate[ 'verrouillee' ] = True


		dates.append( uneDate )
	
	if soldeCarte < tarifRepas :
		soldeInsuffisant = True
	else :
		soldeInsuffisant = False
	jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]


	
	return render_template( 'vueListeReservations.html' , laSession = session , leSolde = solde , lesDates = dates , soldeInsuffisant = soldeInsuffisant , lesJours = jours )

	
@app.route( '/usager/reservations/annuler/<dateISO>' , methods = [ 'GET' ] )
def annulerReservation( dateISO ) :
	modeleResanet.annulerReservation( session[ 'numeroCarte' ] , dateISO )
	modeleResanet.crediterSolde( session[ 'numeroCarte' ] )
	return redirect( '/usager/reservations/lister' )
	
@app.route( '/usager/reservations/enregistrer/<dateISO>' , methods = [ 'GET' ] )
def enregistrerReservation( dateISO ) :
	modeleResanet.enregistrerReservation( session[ 'numeroCarte' ] , dateISO )
	modeleResanet.debiterSolde( session[ 'numeroCarte' ] )
	return redirect( '/usager/reservations/lister' )

@app.route( '/usager/mdp/modification/choisir' , methods = [ 'GET' ] )
def choisirModifierMdpUsager() :
	soldeCarte = modeleResanet.getSolde( session[ 'numeroCarte' ] )
	solde = '%.2f' % ( soldeCarte , )
	
	return render_template( 'vueModificationMdp.html' , laSession = session , leSolde = solde , modifMdp = '' )

@app.route( '/usager/mdp/modification/appliquer' , methods = [ 'POST' ] )
def modifierMdpUsager() :
	ancienMdp = request.form[ 'ancienMDP' ]
	nouveauMdp = request.form[ 'nouveauMDP' ]
	
	soldeCarte = modeleResanet.getSolde( session[ 'numeroCarte' ] )
	solde = '%.2f' % ( soldeCarte , )
	
	if ancienMdp != session[ 'mdp' ] or nouveauMdp == '' :
		return render_template( 'vueModificationMdp.html' , laSession = session , leSolde = solde , modifMdp = 'Nok' )
		
	else :
		modeleResanet.modifierMdpUsager( session[ 'numeroCarte' ] , nouveauMdp )
		session[ 'mdp' ] = nouveauMdp
		return render_template( 'vueModificationMdp.html' , laSession = session , leSolde = solde , modifMdp = 'Ok' )


@app.route( '/gestionnaire/session/choisir' , methods = [ 'GET' ] )
def choisirSessionGestionnaire() :
	return render_template('vueConnexionGestionnaire.html')

@app.route( '/gestionnaire/seConnecter' , methods = [ 'POST' ] )
def seConnecterGestionnaire() :
	login = request.form['login']
	mdp = request.form['mdp']

	if login != '' and mdp != '':
		gestionnaire = modeleResanet.seConnecterGestionnaire(login, mdp)
		personnel = modeleResanet.getPersonnelsAvecCarte()
		if len(gestionnaire) != 0:

			session['nom'] = gestionnaire['nom']
			session['prenom'] = gestionnaire['prenom']
			session['mdp'] = mdp

			return render_template('vuePersonnelAvecCarte.html' , personnel = personnel ,  nbPersonnel = len(personnel))


		else:
			return render_template('vueConnexionGestionnaire.html', carteBloquee=False, echecConnexion=True,
								   saisieIncomplete=False)
	else:
		return render_template('vueConnexionGestionnaire.html', carteBloquee=False, echecConnexion=False,
							 saisieIncomplete=True)

@app.route( '/gestionnaire/seConnecter/lister' , methods = [ 'GET' ] )
def choisirEnteteGestionnaire() :
	return render_template('vueEnteteGestionnaire.html')

@app.route( '/gestionnaire/seDeconnecter' , methods = [ 'GET' ] )
def seDeconnecterGestionnaire() :
	session.pop( 'login' , None )
	session.pop( 'nom' , None )
	session.pop( 'prenom' , None )
	return redirect( '/' )

@app.route( '/gestionnaire/seConnecter/AvecCarte' , methods = [ 'GET' ] )
def choisirPersonnelAvecCarte() :
	personnel = modeleResanet.getPersonnelsAvecCarte()

	return render_template('vuePersonnelAvecCarte.html' , personnel = personnel ,  nbPersonnel = len(personnel))

@app.route( '/gestionnaire/seConnecter/SansCarte' , methods = [ 'GET' ] )
def choisirPersonnelSansCarte() :
	personnel = modeleResanet.getPersonnelsSansCarte()

	return render_template('vuePersonnelSansCarte.html' , personnel = personnel ,  nbPersonnel = len(personnel))

@app.route( '/gestionnaire/seConnecter/AvecCarte/Bloquer/<numeroCarte>' , methods = [ 'GET' ] )
def BloquerCarte(numeroCarte):

	bloquer = modeleResanet.bloquerCarte(numeroCarte)


	return redirect('/gestionnaire/seConnecter/AvecCarte')

@app.route( '/gestionnaire/seConnecter/AvecCarte/Activer/<numeroCarte>' , methods = [ 'GET' ] )
def ActiverCarte(numeroCarte):

	activer = modeleResanet.activerCarte(numeroCarte)


	return redirect('/gestionnaire/seConnecter/AvecCarte')

@app.route( '/gestionnaire/seConnecter/AvecCarte/ReinitialiserMdp/<numeroCarte>' , methods = [ 'GET' ] )
def ReinitialiserMdp(numeroCarte):

	reinitialiser = modeleResanet.reinitialiserMdp(numeroCarte)

	return redirect('/gestionnaire/seConnecter/AvecCarte' )

@app.route( '/gestionnaire/seConnecter/SansCarte/creerCarte/<numeroCarte>' , methods = [ 'POST' ] )
def creerCarte( numeroCarte ) :

	activee = False

	if request.form.get('activer') == '1' :
		activee = True

	modeleResanet.creerCarte(numeroCarte , activee)


	return redirect('/gestionnaire/seConnecter/SansCarte')

@app.route( '/gestionnaire/seConnecter/AvecCarte/Crediter/<numeroCarte>' , methods = [ 'POST' ] )
def CrediterCompte(numeroCarte):

	somme = request.form['Crediter']
	modeleResanet.crediterCarte(numeroCarte,somme)

	return redirect('/gestionnaire/seConnecter/AvecCarte' )



@app.route( '/gestionnaire/seConnecter/pourUneDate', methods = [ 'GET' , 'POST' ] )
def getDateReservation() :
   date = request.values.get('date')
   personnels = []
   if date != 0 :
      personnels = modeleResanet.getReservationsDate(date)
      return render_template( 'vueHistoriqueDate.html', data = personnels)
   else:
      return redirect('/')

@app.route( '/gestionnaire/seConnecter/pourUneCarte', methods = [ 'GET' , 'POST' ] )
def getPersonnelReservation() :
   matricule = request.values.get('matricule')
   debut = request.values.get('debut')
   fin = request.values.get('fin')
   date = []
   if matricule != 0 :
      date = modeleResanet.getReservationsCarte(matricule, debut, fin)
      print(date )
      return render_template( 'vueHistoriqueCarte.html', data = date )
   else:
      return redirect('/')


if __name__ == '__main__' :
	app.run( debug = True , host = '0.0.0.0' , port = 5000 )