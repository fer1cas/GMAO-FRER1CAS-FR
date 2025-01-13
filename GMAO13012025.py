import os
import json
import glob
import streamlit as st
import pandas as pd

# Liste des pays en Afrique
payees_afrique = [
    'Morocco', 'Tunisia', 'Algeria', 'Angola', 'Ivory Cost', 'Mauritania', 'Togo', 'Guinea', 'Mali', 'Senegal', 'Tchad', 'Gabon', 'Cameroun', 'Burkina Faso', 'Congo'
]

# Base de données des clients et des interventions
CLIENTS_DB = "clients.json"
INTERVENTIONS_DB = "interventions.json"  # Fichier pour stocker les interventions
PASSWORD = "0000"  # Mot de passe pour les modifications

# Nouvelle base de données pour l'enregistrement des fichiers JSON
base_path = "Z:\\TT_Work\\TT_Common\\TEST GMAO"  # Remplacez  par le chemin souhaité

# Charger les clients existants
def load_clients():
    if os.path.exists(os.path.join(base_path, CLIENTS_DB)):
        with open(os.path.join(base_path, CLIENTS_DB), 'r') as f:
            return json.load(f)
    return {}

# Charger les interventions existantes
def load_interventions():
    if os.path.exists(os.path.join(base_path, INTERVENTIONS_DB)):
        with open(os.path.join(base_path, INTERVENTIONS_DB), 'r') as f:
            return json.load(f)
    return []

# Sauvegarder les clients
def save_clients(clients):
    with open(os.path.join(base_path, CLIENTS_DB), 'w') as f:
        json.dump(clients, f, indent=4)

# Sauvegarder les interventions
def save_interventions(interventions):
    with open(os.path.join(base_path, INTERVENTIONS_DB), 'w') as f:
        json.dump(interventions, f, indent=4)



# Vérifier si le client existe déjà
def client_exists(base_path, client_name, payee_name, classification):
    client_path = os.path.join(base_path, classification, payee_name, client_name)
    return os.path.exists(client_path)

# Création de structure des dossiers
def create_structure(base_path, payee_name, client_name, year, classification):
    classification_path = os.path.join(base_path, classification)
    os.makedirs(classification_path, exist_ok=True)

    payee_path = os.path.join(classification_path, payee_name)
    os.makedirs(payee_path, exist_ok=True)

    client_path = os.path.join(payee_path, client_name)
    os.makedirs(client_path, exist_ok=True)

    for month in range(1, 13):
        month_str = f"{month:02d}"
        month_path = os.path.join(client_path, month_str)
        os.makedirs(month_path, exist_ok=True)

        for doc_type in [
            "Rapport_intervention", "Offre_service", "Offre_PDR",
            "BC_service", "BC_PDR", "Documentation"
        ]:
            os.makedirs(os.path.join(month_path, doc_type), exist_ok=True)

# Interface pour créer un client avec des informations supplémentaires
def create_client():
    st.header("Créer un client")
    clients = load_clients()

    base_path = "Z:\\TT_Work\\TT_Common\\TEST GMAO"

    client_name = st.text_input('Nom du client')
    payee_name = st.selectbox('Sélectionner la payée en Afrique', payees_afrique)
    classification = st.selectbox('Sélectionner la classification du client', ['Sacofrina', 'Others'])

    address = st.text_input('Adresse')
    contact = st.text_input('Contact')
    email = st.text_input('Email')
    secteur = st.selectbox('Secteur d\'activité', ['Agro', 'Textil', 'Raffinage'])

    num_chaudieres = st.number_input('Nombre de chaudières', min_value=1, step=1)
    chaudiere_serial_numbers = []
    for i in range(num_chaudieres):
        serial_number = st.text_input(f'Numéro de série de la chaudière {i+1}')
        if serial_number:
            chaudiere_serial_numbers.append(serial_number)

    burner_type = st.selectbox('Type de brûleur', ['Saacke SKVA', 'Saacke SKVGA', 'Weishaupt'])

    if st.button('Créer le client'):
        if client_exists(base_path, client_name, payee_name, classification):
            st.warning(f"Le client '{client_name}' existe déjà dans le chemin spécifié.")
        elif client_name and payee_name:
            create_structure(base_path, payee_name, client_name, 2024, classification)
            clients[client_name] = {
                "payee": payee_name, "address": address, "contact": contact,
                "email": email, "secteur": secteur,
                "num_chaudieres": num_chaudieres,
                "chaudiere_serial_numbers": chaudiere_serial_numbers,
                "burner_type": burner_type
            }
            save_clients(clients)
            st.success(f"Client {client_name} créé avec succès dans la payée {payee_name}.")
        else:
            st.error("Veuillez remplir tous les champs obligatoires.")

# Interface pour ajouter des rapports ou des offres
def add_document(doc_type):
    st.header(f"Ajouter un(e) {doc_type}")
    clients = load_clients()

    if not clients:
        st.warning("Aucun client disponible.")
        return

    client_name = st.selectbox('Sélectionner le client', list(clients.keys()))
    payee_name = st.selectbox('Sélectionner la payée en Afrique', payees_afrique)
    classification = st.selectbox('Sélectionner la classification du client', ['Sacofrina', 'Others'])

    if client_name and payee_name:
        correct_payee = clients[client_name]["payee"]
        if correct_payee != payee_name:
            st.error(f"Erreur : Le client '{client_name}' appartient à la payée '{correct_payee}', et non à '{payee_name}'. Veuillez corriger votre sélection.")
            return

    month = st.selectbox('Sélectionner le mois', [str(i).zfill(2) for i in range(1, 13)])

    if doc_type == "BC_service" or doc_type == "BC_PDR":
        # Add section for BC
        st.subheader("Ajouter un Bon de Commande (BC)")
        
        # Select existing offer
        offer_type = st.selectbox("Sélectionner le type d'offre", ["Offre_service", "Offre_PDR"])
        offer_month = st.selectbox('Sélectionner le mois de l\'offre', [str(i).zfill(2) for i in range(1, 13)])
        
        # Check if offer exists
        offer_path = os.path.join("Z:\\TT_Work\\TT_Common\\TEST GMAO", classification, payee_name, client_name, offer_month, offer_type)
        if os.path.exists(offer_path):
            offers = glob.glob(os.path.join(offer_path, '*'))
            offer_selection = st.selectbox("Sélectionner une offre", offers)
        else:
            st.warning("Aucune offre trouvée pour ce client et ce mois.")
            return
        
        # Upload BC file
        doc_file = st.file_uploader(f'Télécharger le fichier {doc_type}', type=['pdf', 'docx', 'jpg'])
        
        if st.button(f'Ajouter le/la {doc_type}'):
            if doc_file:
                save_path = os.path.join(
                    "Z:\\TT_Work\\TT_Common\\TEST GMAO", classification, payee_name, client_name, month, doc_type, doc_file.name
                )
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(save_path, 'wb') as f:
                    f.write(doc_file.getbuffer())
                st.success(f"{doc_type} ajouté(e) pour le client {client_name}, mois {month}. Lien avec l'offre : {offer_selection}.")
            else:
                st.error(f"Veuillez télécharger un fichier pour le/la {doc_type}.")
    else:
        # Original document upload process for other types
        doc_file = st.file_uploader(f'Télécharger le fichier {doc_type}', type=['pdf', 'docx', 'jpg'])

        if st.button(f'Ajouter le/la {doc_type}'):
            if doc_file:
                save_path = os.path.join(
                    "Z:\\TT_Work\\TT_Common\\TEST GMAO", classification, payee_name, client_name, month, doc_type, doc_file.name
                )
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(save_path, 'wb') as f:
                    f.write(doc_file.getbuffer())
                st.success(f"{doc_type} ajouté(e) pour le client {client_name}, mois {month}.")
            else:
                st.error(f"Veuillez télécharger un fichier pour le/la {doc_type}.")

# Interface pour modifier les données d'un client
def modify_client():
    st.header("Modifier les données d'un client")
    clients = load_clients()

    if not clients:
        st.warning("Aucun client disponible.")
        return

    client_name = st.selectbox('Sélectionner le client à modifier', list(clients.keys()))
    if client_name:
        payee_name = st.text_input('Nouvelle payée', clients[client_name]["payee"])
        address = st.text_input('Nouvelle adresse', clients[client_name]["address"])
        contact = st.text_input('Nouveau contact', clients[client_name]["contact"])
        email = st.text_input('Nouvel email', clients[client_name]["email"])

        secteurs = ['Agro', 'Textil', 'Raffinage']
        secteur = st.selectbox('Nouveau secteur d\'activité', secteurs, index=secteurs.index(clients[client_name]["secteur"]) if clients[client_name]["secteur"] in secteurs else 0)

        num_chaudieres = st.number_input('Nombre de chaudières', min_value=1, step=1, value=clients[client_name].get("num_chaudieres", 1))
        chaudiere_serial_numbers = clients[client_name].get("chaudiere_serial_numbers", [])

        # Define burner types
        burner_types = ['Saacke SKVA', 'Saacke SKVGA', 'Weishaupt']
        # Get the current burner type or default to the first option if not found
        current_burner_type = clients[client_name].get("burner_type", burner_types[0])
        if current_burner_type not in burner_types:
            current_burner_type = burner_types[0]  # Fallback to the first option if not found

        burner_type = st.selectbox('Type de brûleur', burner_types, index=burner_types.index(current_burner_type))

        password = st.text_input("Mot de passe", type="password")

        if st.button("Sauvegarder les modifications"):
            if password == PASSWORD:
                clients[client_name] = {
                    "payee": payee_name, "address": address, "contact": contact,
                    "email": email, "secteur": secteur,
                    "num_chaudieres": num_chaudieres,
                    "chaudiere_serial_numbers": chaudiere_serial_numbers,
                    "burner_type": burner_type
                }
                save_clients(clients)
                st.success(f"Données du client '{client_name}' mises à jour avec succès.")
            else:
                st.error("Mot de passe incorrect.")

        if st.button("Supprimer le client"):
            if password == PASSWORD:
                del clients[client_name]
                save_clients(clients)
                st.success(f"Client '{client_name}' supprimé avec succès.")
            else:
                st.error("Mot de passe incorrect.")




# Interface pour rechercher rapidement des offres
def quick_search_offers():
    st.header("Recherche Rapide des Offres")
    clients = load_clients()

    if not clients:
        st.warning("Aucun client disponible.")
        return

    selected_payees = st.multiselect('Sélectionner les payées', payees_afrique)
    selected_clients = st.multiselect('Sélectionner les clients', list(clients.keys()))
    doc_type = st.selectbox("Type d'offre à rechercher", ["Rapport_intervention", "Offre_service", "Offre_PDR"])
    start_month = st.text_input('Mois de début (01-12)', "01")
    end_month = st.text_input('Mois de fin (01-12)', "12")

    if st.button('Rechercher'):
        results = []
        for payee in selected_payees:
            for client in selected_clients:
                for month in range(int(start_month), int(end_month) + 1):
                    month_str = str(month).zfill(2)
                    for classification in ['Sacofrina', 'Others']:
                        doc_path = os.path.join("Z:\\TT_Work\\TT_Common\\TEST GMAO", classification, payee, client, month_str, doc_type)
                        if os.path.exists(doc_path):
                            documents = glob.glob(os.path.join(doc_path, '*'))
                            for document in documents:
                                results.append({
                                    "Client": client,
                                    "Date": f"{month_str}/2024",  # Ajout de l'année pour la date
                                    "Type": doc_type,
                                    "Fichier": document
                                })

        if results:
            df_results = pd.DataFrame(results)
            st.dataframe(df_results)  # Afficher le tableau des résultats
        else:
            st.warning(f"Aucun {doc_type} trouvé dans la période sélectionnée.")

# Interface pour le Bilan des Offres et BC
def bilan_offres_bc():
    st.header("Bilan des Offres et BC")

    clients = load_clients()

    if not clients:
        st.warning("Aucun client disponible.")
        return

    selected_payees = st.multiselect('Sélectionner les payées', payees_afrique)
    selected_clients = st.multiselect('Sélectionner les clients', list(clients.keys()))
    doc_type = st.selectbox("Sélectionner le type d'offre", ["Offre_service", "Offre_PDR", "BC_service", "BC_PDR"])

    start_month = st.text_input('Mois de début (01-12)', "01")
    end_month = st.text_input('Mois de fin (01-12)', "12")

    if st.button('Générer le bilan'):
        month_counts = {str(i).zfill(2): 0 for i in range(1, 13)}
        results = []

        for payee in selected_payees:
            for client in selected_clients:
                for month in range(int(start_month), int(end_month) + 1):
                    month_str = str(month).zfill(2)
                    for classification in ['Sacofrina', 'Others']:
                        doc_path = os.path.join("Z:\\TT_Work\\TT_Common\\TEST GMAO", classification, payee, client, month_str, doc_type)
                        if os.path.exists(doc_path):
                            documents = glob.glob(os.path.join(doc_path, '*'))
                            count = len(documents)
                            month_counts[month_str] += count

                            # Ajouter les résultats pour le tableau
                            for document in documents:
                                results.append({
                                    "Client": client,
                                    "Date": f"{month_str}/2024",  # Ajout de l'année pour la date
                                    "Type": doc_type,
                                    "Nombre": count,
                                    "Fichier": document
                                })

        # Afficher les résultats dans un tableau
        if results:
            df_results = pd.DataFrame(results)
            st.dataframe(df_results)  # Afficher le tableau des résultats

        else:
            st.warning(f"Aucun {doc_type} trouvé pour la période sélectionnée.")

# Interface pour afficher les clients sous forme de tableau
def display_clients():
    st.header("Liste des Clients")
    clients = load_clients()

    if not clients:
        st.warning("Aucun client disponible.")
        return

    # Convertir les données des clients en DataFrame
    data = []
    for client_name, info in clients.items():
        data.append({
            "Nom du Client": client_name,
            "Payée": info["payee"],
            "Adresse": info["address"],
            "Contact": info["contact"],
            "Email": info["email"],
            "Secteur": info["secteur"],
            "Nombre de Chaudières": info["num_chaudieres"],
            "Type de Brûleur": info["burner_type"],
            "Numéros de Série des Chaudières": ", ".join(info["chaudiere_serial_numbers"])  # Ajouter les numéros de série
        })

    df = pd.DataFrame(data)

    # Filtrer par payée
    selected_payee = st.selectbox("Filtrer par payée", ['Tous'] + payees_afrique)
    if selected_payee != 'Tous':
        df = df[df["Payée"] == selected_payee]

    st.dataframe(df)  # Afficher le tableau

# Ajout de la fonction pour la planification des interventions
def planification_interventions():
    st.header("Planification des Interventions")
    clients = load_clients()

    if not clients:
        st.warning("Aucun client disponible.")
        return

    client_name = st.selectbox('Sélectionner le client', list(clients.keys()))
    payee_name = st.selectbox('Sélectionner la payée en Afrique', payees_afrique)

    if client_name:
        correct_payee = clients[client_name]["payee"]
        if correct_payee != payee_name:
            st.error(f"Erreur : Le client '{client_name}' appartient à la payée '{correct_payee}', et non à '{payee_name}'. Veuillez corriger votre sélection.")
            return

    date_debut = st.date_input('Date de début d\'intervention')
    date_fin = st.date_input('Date de fin d\'intervention')

    if date_fin < date_debut:
        st.error("La date de fin doit être après la date de début.")
        return

    type_intervention = st.selectbox('Type d\'intervention', [
        'Maintenance préventive', 'Maintenance corrective', 
        'Mise en service', 'Audit énergétique', 'Autre'
    ])

    technicien = st.selectbox('Choisir le technicien', [
        'Ferjeni Ramzi', 'El Mahi Mouhcine', 
        'Marzouk Abdelhadi', 'El Najjar Abdessamad', 'Moustafa'
    ])

    statut = st.selectbox('Statut de l\'intervention', ['Confirmer', 'Planifier', 'Proposer'])

    # Calculer le nombre de jours d'intervention
    nb_jours_intervention = (date_fin - date_debut).days + 1

    if st.button('Planifier l\'intervention'):
        # Enregistrer l'intervention
        interventions = load_interventions()
        new_intervention = {
            "Client": client_name,
            "Payée": payee_name,
            "Date de début": str(date_debut),
            "Date de fin": str(date_fin),
            "Nombre de jours d'intervention": nb_jours_intervention,
            "Technicien": technicien,
            "Statut": statut
        }
        interventions.append(new_intervention)
        save_interventions(interventions)

        st.success(f"Intervention planifiée avec succès !\n"
                   f"Client : {client_name}\n"
                   f"Payée : {payee_name}\n"
                   f"Date de début : {date_debut}\n"
                   f"Date de fin : {date_fin}\n"
                   f"Type d'intervention : {type_intervention}\n"
                   f"Technicien : {technicien}\n"
                   f"Nombre de jours d'intervention : {nb_jours_intervention}")

# Fonction pour afficher le bilan des interventions

def bilan_interventions():
    st.header("Bilan des Interventions")
    interventions = load_interventions()

    if not interventions:
        st.warning("Aucune intervention disponible.")
        return

    clients = load_clients()
    client_names = list(clients.keys())
    selected_clients = st.multiselect('Sélectionner les clients', client_names)

    # Filtrer les interventions par clients sélectionnés
    filtered_interventions = [
        inv for inv in interventions if inv["Client"] in selected_clients
    ] if selected_clients else interventions

    if filtered_interventions:
        df_interventions = pd.DataFrame(filtered_interventions)
        st.dataframe(df_interventions)  # Afficher le tableau des interventions

        # Sélectionner une intervention à modifier ou supprimer
        intervention_to_modify = st.selectbox("Sélectionner une intervention à modifier ou supprimer", filtered_interventions)

        # Afficher les détails de l'intervention sélectionnée
        if intervention_to_modify:
            current_date_debut = pd.to_datetime(intervention_to_modify["Date de début"])
            current_date_fin = pd.to_datetime(intervention_to_modify["Date de fin"])
            current_statut = intervention_to_modify["Statut"]
            current_technicien = intervention_to_modify["Technicien"]

            # Modifier les dates
            new_date_debut = st.date_input("Nouvelle date de début", current_date_debut)
            new_date_fin = st.date_input("Nouvelle date de fin", current_date_fin)

            # Modifier le statut
            new_statut = st.selectbox('Nouveau statut de l\'intervention', ['Confirmer', 'Planifier', 'Proposer'], index=['Confirmer', 'Planifier', 'Proposer'].index(current_statut))

            # Modifier le technicien
            new_technicien = st.selectbox('Nouveau technicien', [
                'Ferjeni Ramzi', 'El Mahi Mouhcine', 
                'Marzouk Abdelhadi', 'El Najjar Abdessamad', 'Moustafa'
            ], index=['Ferjeni Ramzi', 'El Mahi Mouhcine', 'Marzouk Abdelhadi', 'El Najjar Abdessamad', 'Moustafa'].index(current_technicien))

            password = st.text_input("Mot de passe", type="password")

            if st.button("Sauvegarder les modifications"):
                if password == PASSWORD:
                    # Mettre à jour l'intervention
                    intervention_to_modify["Date de début"] = str(new_date_debut)
                    intervention_to_modify["Date de fin"] = str(new_date_fin)
                    intervention_to_modify["Statut"] = new_statut
                    intervention_to_modify["Technicien"] = new_technicien

                    # Sauvegarder les interventions mises à jour
                    save_interventions(interventions)
                    st.success("Intervention mise à jour avec succès.")
                else:
                    st.error("Mot de passe incorrect.")

            # Option pour supprimer l'intervention
            if st.button("Supprimer l'intervention"):
                if password == PASSWORD:
                    interventions.remove(intervention_to_modify)
                    save_interventions(interventions)
                    st.success("Intervention supprimée avec succès.")
                else:
                    st.error("Mot de passe incorrect.")
    else:
        st.warning("Aucune intervention trouvée pour les clients sélectionnés.")




# Fonction principale pour le menu
def main():
    st.title("Gestion des Clients et Interventions")
    menu = [
        "Créer Client", 
        "Ajouter Document", 
        "Modifier Client",  
        "Recherche Offres", 
        "Bilan Offres", 
        "Afficher Clients",
        "Planification Interventions",
        "Bilan des Interventions"
    ]
    
    choice = st.sidebar.selectbox("Sélectionner une option", menu)

    if choice == "Créer Client":
        create_client()
    elif choice == "Ajouter Document":
        doc_type = st.selectbox("Sélectionner le type de document", ["Rapport_intervention", "Offre_service", "Offre_PDR", "BC_service", "BC_PDR"])
        add_document(doc_type)
    elif choice == "Modifier Client":
        modify_client()
    elif choice == "Recherche Offres":
        quick_search_offers()
    elif choice == "Bilan Offres":
        bilan_offres_bc()
    elif choice == "Afficher Clients":
        display_clients()
    elif choice == "Planification Interventions":
        planification_interventions()
    elif choice == "Bilan des Interventions":
        bilan_interventions()

if __name__ == "__main__":
    main()
