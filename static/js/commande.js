// Order management functionality

class OrderManager {
    constructor() {
        this.paires = [];
        this.prestations = {};
        this.currentStep = 1;
        this.currentPaireIndex = -1;
        this.storageKey = 'conciergerie_commande_draft';

        this.initializeElements();
        this.bindEvents();
        this.loadPrestationsFromTemplate();

        // Load saved data or create first pair
        this.loadFromStorage();
    }

    initializeElements() {
        this.paireContainer = document.getElementById('paires-container');
        this.btnAjouterPaire = document.getElementById('btn-ajouter-paire');
        this.btnValiderPaires = document.getElementById('btn-valider-paires');
        this.btnRetourPaires = document.getElementById('btn-retour-paires');
        this.btnAllerPaiement = document.getElementById('btn-aller-paiement');
        this.btnRetourValidation = document.getElementById('btn-retour-validation');

        this.recapContainer = document.getElementById('recapitulatif-container');
        this.totalCommande = document.getElementById('total-commande');
        this.resumePaiement = document.getElementById('resume-paiement');
        this.totalFinal = document.getElementById('total-final');

        this.formCommande = document.getElementById('form-commande');
        this.btnPayer = document.getElementById('btn-payer');

        this.photoModal = new bootstrap.Modal(document.getElementById('photoModal'));
        this.confirmPhotoBtn = document.getElementById('btn-confirm-photo');
    }

    bindEvents() {
        if (this.btnAjouterPaire) {
            this.btnAjouterPaire.addEventListener('click', () => this.ajouterPaire());
        }

        if (this.btnValiderPaires) {
            this.btnValiderPaires.addEventListener('click', () => this.validerPaires());
        }

        if (this.btnRetourPaires) {
            this.btnRetourPaires.addEventListener('click', () => this.allerEtape(1));
        }

        if (this.btnAllerPaiement) {
            this.btnAllerPaiement.addEventListener('click', () => this.allerEtape(3));
        }

        if (this.btnRetourValidation) {
            this.btnRetourValidation.addEventListener('click', () => this.allerEtape(2));
        }

        if (this.confirmPhotoBtn) {
            this.confirmPhotoBtn.addEventListener('click', () => this.confirmerPhoto());
        }

        if (this.formCommande) {
            this.formCommande.addEventListener('submit', (e) => this.traiterCommande(e));
        }

        // Listen for form input changes
        if (this.formCommande) {
            this.formCommande.addEventListener('input', () => {
                this.validatePaymentForm();
                this.saveToStorage(); // Save client info as user types
            });
        }
    }

    loadPrestationsFromTemplate() {
        // Récupérer les prestations depuis les variables globales injectées par le template
        if (window.prestationsHomme && window.prestationsFemme) {
            this.prestations = {
                HOMME: window.prestationsHomme,
                FEMME: window.prestationsFemme
            };
        } else {
            console.warn('Prestations not found in template variables');
            this.prestations = {
                HOMME: [],
                FEMME: []
            };
        }
    }

    ajouterPaire() {
        const index = this.paires.length;
        const paire = {
            id: `paire-${Date.now()}-${index}`,
            type_chaussure: '',
            photo_url: '',
            photo_filename: '',
            prestations: [],
            description: ''
        };

        this.paires.push(paire);
        this.renderPaire(paire, index);
        this.updateValidationButton();
        this.saveToStorage();

        // Scroll to new paire
        setTimeout(() => {
            const newPaireElement = document.querySelector(`[data-paire-id="${paire.id}"]`);
            if (newPaireElement) {
                newPaireElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }, 100);
    }

    renderPaire(paire, index) {
        const isValidated = paire.validated;
        const isCollapsed = paire.collapsed;

        const paireHtml = `
            <div class="paire-card ${isValidated ? 'validated' : ''} ${isCollapsed ? 'collapsed' : ''}" data-paire-id="${paire.id}">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h6 class="mb-0">Paire ${index + 1}</h6>
                    <div class="btn-group">
                        ${isValidated ? `
                            <button type="button" class="btn btn-outline-primary btn-sm" onclick="orderManager.editerPaire('${paire.id}')" style="display: ${isCollapsed ? 'inline-block' : 'none'};">
                                <i class="bi bi-pencil"></i>
                            </button>
                        ` : ''}
                        <button type="button" class="btn btn-outline-danger btn-sm" onclick="orderManager.supprimerPaire('${paire.id}')">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>

                <!-- Collapsed view for validated pairs -->
                ${isValidated && isCollapsed ? `
                    <div class="collapsed-view">
                        <div class="row align-items-center">
                            <div class="col-3">
                                <img src="${paire.photo_url}" class="img-fluid rounded" alt="Paire ${index + 1}" style="max-height: 60px; object-fit: cover;">
                            </div>
                            <div class="col-9">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <span class="badge bg-primary">${paire.type_chaussure === 'HOMME' ? 'Homme' : 'Femme'}</span>
                                        <span class="ms-2">${this.getSelectedServicesNames(paire).join(', ')}</span>
                                    </div>
                                    <span class="badge bg-success"><i class="bi bi-check-circle me-1"></i>Validée</span>
                                </div>
                            </div>
                        </div>
                    </div>
                ` : ''}

                <!-- Full view -->
                <div class="full-view" style="display: ${isValidated && isCollapsed ? 'none' : 'block'};">
                    <div class="row g-3">
                        <!-- Type et services -->
                        <div class="col-12">
                            <!-- Type de chaussure -->
                            <div class="mb-3">
                                <label class="form-label">Type de chaussure *</label>
                                <div class="btn-group w-100" role="group">
                                    <input type="radio" class="btn-check" name="type-${paire.id}" id="homme-${paire.id}" value="HOMME" ${paire.type_chaussure === 'HOMME' ? 'checked' : ''}>
                                    <label class="btn btn-outline-primary" for="homme-${paire.id}">Homme</label>

                                    <input type="radio" class="btn-check" name="type-${paire.id}" id="femme-${paire.id}" value="FEMME" ${paire.type_chaussure === 'FEMME' ? 'checked' : ''}>
                                    <label class="btn btn-outline-primary" for="femme-${paire.id}">Femme</label>
                                </div>
                            </div>

                            <!-- Services -->
                            <div class="mb-3">
                                <label class="form-label">Services *</label>
                                <div id="services-${paire.id}">
                                    ${this.renderServices(paire)}
                                </div>
                            </div>

                            <!-- Description optionnelle -->
                            <div class="mb-3" id="description-container-${paire.id}" style="display: none;">
                                <label class="form-label">Description (requis pour devis)</label>
                                <textarea class="form-control" id="description-${paire.id}" rows="2" placeholder="Décrivez les détails pour le devis...">${paire.description}</textarea>
                            </div>

                            <!-- Photo -->
                            <div class="mb-3" id="photo-container-${paire.id}" style="display: ${paire.prestations.length > 0 ? 'block' : 'none'};">
                                <label class="form-label">Photo de la paire *</label>
                                <div class="photo-upload-area ${paire.photo_url ? 'has-photo' : ''}" onclick="orderManager.ouvrirCamera('${paire.id}')">
                                    ${paire.photo_url ?
                                        `<img src="${paire.photo_url}" class="paire-photo" alt="Photo paire ${index + 1}">` :
                                        `<div>
                                            <i class="bi bi-camera fs-1 text-muted mb-2"></i>
                                            <p class="text-muted mb-0">Prendre une photo</p>
                                            <small class="text-muted">Obligatoire</small>
                                        </div>`
                                    }
                                </div>
                            </div>

                            <!-- Bouton de validation de la paire -->
                            <div class="text-center mb-3">
                                <button type="button"
                                        class="btn btn-success btn-lg paire-validate-btn w-75"
                                        id="validate-${paire.id}"
                                        onclick="orderManager.validerPaire('${paire.id}')"
                                        disabled>
                                    <i class="bi bi-check-circle me-2"></i>Valider cette paire
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.paireContainer.insertAdjacentHTML('beforeend', paireHtml);

        // Bind events for this paire
        this.bindPaireEvents(paire.id);

        // Update validation button state
        this.updatePaireValidationButton(paire.id);

        // Update description field visibility
        this.updateDescriptionVisibility(paire.id);

        // Update photo field visibility
        this.updatePhotoVisibility(paire.id);
    }

    bindPaireEvents(paireId) {
        // Type de chaussure change
        const typeRadios = document.querySelectorAll(`input[name="type-${paireId}"]`);
        typeRadios.forEach(radio => {
            radio.addEventListener('change', () => {
                const paire = this.paires.find(p => p.id === paireId);
                if (paire) {
                    paire.type_chaussure = radio.value;
                    paire.prestations = []; // Reset prestations when type changes
                    this.updateServicesForPaire(paireId);
                    this.updatePaireValidationButton(paireId);
                    this.updateValidationButton();
                    this.updatePhotoVisibility(paireId);
                    this.saveToStorage();
                }
            });
        });

        // Description change
        const descriptionTextarea = document.getElementById(`description-${paireId}`);
        if (descriptionTextarea) {
            descriptionTextarea.addEventListener('input', () => {
                const paire = this.paires.find(p => p.id === paireId);
                if (paire) {
                    paire.description = descriptionTextarea.value;
                    this.saveToStorage();
                }
            });
        }
    }

    renderServices(paire) {
        if (!paire.type_chaussure || !this.prestations[paire.type_chaussure]) {
            return '<p class="text-muted">Sélectionnez d\'abord le type de chaussure</p>';
        }

        const services = this.prestations[paire.type_chaussure];
        return services.map(service => `
            <div class="service-checkbox">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" value="${service.id}"
                           id="service-${paire.id}-${service.id}"
                           ${paire.prestations.includes(service.id) ? 'checked' : ''}
                           onchange="orderManager.toggleService('${paire.id}', ${service.id})">
                    <label class="form-check-label d-flex justify-content-between w-100" for="service-${paire.id}-${service.id}">
                        <span>
                            <strong>${service.nom}</strong>
                            ${service.description ? `<br><small class="text-muted">${service.description}</small>` : ''}
                        </span>
                        <span class="service-price">${formatPrice(service.prix)}</span>
                    </label>
                </div>
            </div>
        `).join('');
    }

    updateServicesForPaire(paireId) {
        const servicesContainer = document.getElementById(`services-${paireId}`);
        const paire = this.paires.find(p => p.id === paireId);

        if (servicesContainer && paire) {
            servicesContainer.innerHTML = this.renderServices(paire);
        }
    }

    toggleService(paireId, serviceId) {
        const paire = this.paires.find(p => p.id === paireId);
        if (!paire) return;

        const index = paire.prestations.indexOf(serviceId);
        if (index > -1) {
            paire.prestations.splice(index, 1);
        } else {
            paire.prestations.push(serviceId);
        }

        this.updatePaireValidationButton(paireId);
        this.updateValidationButton();
        this.updateDescriptionVisibility(paireId);
        this.updatePhotoVisibility(paireId);
        this.saveToStorage();
    }

    supprimerPaire(paireId) {
        if (confirm('Êtes-vous sûr de vouloir supprimer cette paire ?')) {
            // Remove from array
            this.paires = this.paires.filter(p => p.id !== paireId);

            // Remove from DOM
            const paireElement = document.querySelector(`[data-paire-id="${paireId}"]`);
            if (paireElement) {
                paireElement.remove();
            }

            // Re-render to update paire numbers
            this.renderAllPaires();

            // Update validation button
            this.updateValidationButton();
            this.saveToStorage();
        }
    }

    renderAllPaires() {
        this.paireContainer.innerHTML = '';
        this.paires.forEach((paire, index) => {
            this.renderPaire(paire, index);
        });
    }

    ouvrirCamera(paireId) {
        this.currentPaireIndex = this.paires.findIndex(p => p.id === paireId);
        this.photoModal.show();
    }

    async confirmerPhoto() {
        if (!cameraManager.hasPhoto()) {
            showToast('Aucune photo sélectionnée', 'error');
            return;
        }

        try {
            showLoading();

            // Compress and upload photo
            const photoDataUrl = cameraManager.getPhotoDataUrl();
            const compressedPhoto = await compressImage(photoDataUrl, 0.8, 1024, 1024);

            const response = await api.uploadPhoto(compressedPhoto);

            // Update paire with photo info
            const paire = this.paires[this.currentPaireIndex];
            if (paire) {
                paire.photo_url = response.photo_url;
                paire.photo_filename = response.filename;

                // Update UI
                this.renderAllPaires();
                this.updateValidationButton();
                this.updatePaireValidationButton(paire.id);
                this.saveToStorage();
            }

            this.photoModal.hide();
            showToast('Photo ajoutée avec succès', 'success');

        } catch (error) {
            console.error('Error uploading photo:', error);
            showToast('Erreur lors de l\'upload de la photo', 'error');
        } finally {
            hideLoading();
        }
    }

    updateValidationButton() {
        // Check if all pairs are validated
        const allPairesValidated = this.paires.length > 0 && this.paires.every(paire => paire.validated);

        // Hide/show "Valider et continuer" button
        if (this.btnValiderPaires) {
            this.btnValiderPaires.style.display = allPairesValidated ? 'inline-block' : 'none';
            this.btnValiderPaires.disabled = !allPairesValidated;
        }

        // Hide/show "Ajouter une paire" button
        if (this.btnAjouterPaire) {
            this.btnAjouterPaire.style.display = allPairesValidated ? 'inline-block' : 'none';
        }
    }

    validerPaires() {
        if (this.paires.length === 0) {
            showToast('Ajoutez au moins une paire de chaussures', 'error');
            return;
        }

        // Validate all paires
        for (let i = 0; i < this.paires.length; i++) {
            const paire = this.paires[i];
            if (!paire.type_chaussure) {
                showToast(`Sélectionnez le type pour la paire ${i + 1}`, 'error');
                return;
            }
            if (!paire.photo_url) {
                showToast(`Ajoutez une photo pour la paire ${i + 1}`, 'error');
                return;
            }
            if (paire.prestations.length === 0) {
                showToast(`Sélectionnez au moins un service pour la paire ${i + 1}`, 'error');
                return;
            }
        }

        this.allerEtape(2);
        this.renderRecapitulatif();
    }

    validerPaire(paireId) {
        const paire = this.paires.find(p => p.id === paireId);
        if (!paire) return;

        // Check if type is selected
        if (!paire.type_chaussure) {
            showToast('Sélectionnez le type de chaussure', 'error');
            return;
        }

        // Check if at least one service is selected
        if (paire.prestations.length === 0) {
            showToast('Sélectionnez au moins un service', 'error');
            return;
        }

        // Check if photo is taken
        if (!paire.photo_url) {
            showToast('Prenez une photo de cette paire', 'error');
            return;
        }

        // Mark pair as validated and collapse it
        paire.validated = true;
        paire.collapsed = true;
        this.renderAllPaires(); // Re-render to show collapsed view
        this.updateValidationButton(); // Update global buttons
        this.saveToStorage();
        showToast('Paire validée avec succès', 'success');
    }

    updatePaireValidationButton(paireId) {
        const paire = this.paires.find(p => p.id === paireId);
        if (!paire) return;

        const button = document.getElementById(`validate-${paireId}`);
        if (!button) return;

        const hasType = !!paire.type_chaussure;
        const hasServices = paire.prestations.length > 0;
        const hasPhoto = !!paire.photo_url;
        const isComplete = hasType && hasServices && hasPhoto;

        button.disabled = !isComplete;

        if (paire.validated) {
            button.classList.remove('btn-success');
            button.classList.add('btn-outline-success');
            button.innerHTML = '<i class="bi bi-check-circle-fill me-2"></i>Paire validée';
            button.disabled = true;
        } else if (isComplete) {
            button.classList.remove('btn-outline-success');
            button.classList.add('btn-success');
            button.innerHTML = '<i class="bi bi-check-circle me-2"></i>Valider cette paire';
        }
    }

    updateDescriptionVisibility(paireId) {
        const paire = this.paires.find(p => p.id === paireId);
        if (!paire) return;

        const descriptionContainer = document.getElementById(`description-container-${paireId}`);
        if (!descriptionContainer) return;

        // Check if any "Autre" service is selected (IDs 13 and 20)
        const hasAutreService = paire.prestations.some(prestationId => {
            const prestation = this.getAllPrestations().find(p => p.id === prestationId);
            return prestation && prestation.nom.includes('Autre');
        });

        // Show or hide the description field
        descriptionContainer.style.display = hasAutreService ? 'block' : 'none';

        // Clear description if hiding the field
        if (!hasAutreService) {
            const descriptionTextarea = document.getElementById(`description-${paireId}`);
            if (descriptionTextarea) {
                descriptionTextarea.value = '';
                paire.description = '';
            }
        }
    }

    updatePhotoVisibility(paireId) {
        const paire = this.paires.find(p => p.id === paireId);
        if (!paire) return;

        const photoContainer = document.getElementById(`photo-container-${paireId}`);
        if (!photoContainer) return;

        // Show photo field only if at least one prestation is selected
        const hasPrestation = paire.prestations.length > 0;
        photoContainer.style.display = hasPrestation ? 'block' : 'none';

        // Clear photo if hiding the field
        if (!hasPrestation) {
            paire.photo_url = '';
            paire.photo_filename = '';
        }
    }

    renderRecapitulatif() {
        let total = 0;
        let recapHtml = '';

        this.paires.forEach((paire, index) => {
            let pairTotal = 0;
            const prestationsHtml = paire.prestations.map(prestationId => {
                const prestation = this.getAllPrestations().find(p => p.id === prestationId);
                if (prestation) {
                    pairTotal += prestation.prix;
                    return `
                        <li class="d-flex justify-content-between">
                            <span>${prestation.nom}</span>
                            <span>${formatPrice(prestation.prix)}</span>
                        </li>
                    `;
                }
                return '';
            }).join('');

            total += pairTotal;

            recapHtml += `
                <div class="card mb-3">
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-3">
                                <img src="${paire.photo_url}" class="img-fluid rounded" alt="Paire ${index + 1}">
                            </div>
                            <div class="col-md-9">
                                <h6>Paire ${index + 1} - ${paire.type_chaussure === 'HOMME' ? 'Homme' : 'Femme'}</h6>
                                ${paire.description ? `<p class="text-muted small">${paire.description}</p>` : ''}
                                <ul class="list-unstyled mb-2">
                                    ${prestationsHtml}
                                </ul>
                                <div class="text-end">
                                    <strong>Sous-total: ${formatPrice(pairTotal)}</strong>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        if (this.recapContainer) {
            this.recapContainer.innerHTML = recapHtml;
        }

        if (this.totalCommande) {
            this.totalCommande.textContent = formatPrice(total);
        }

        if (this.totalFinal) {
            this.totalFinal.textContent = formatPrice(total);
        }

        if (this.resumePaiement) {
            this.resumePaiement.innerHTML = this.generateResumePaiement();
        }
    }

    generateResumePaiement() {
        let resumeHtml = '';
        this.paires.forEach((paire, index) => {
            const prestations = paire.prestations.map(prestationId => {
                const prestation = this.getAllPrestations().find(p => p.id === prestationId);
                return prestation ? prestation.nom : '';
            }).filter(Boolean).join(', ');

            resumeHtml += `
                <div class="mb-2">
                    <small><strong>Paire ${index + 1}</strong> (${paire.type_chaussure === 'HOMME' ? 'Homme' : 'Femme'})</small><br>
                    <small class="text-muted">${prestations}</small>
                </div>
            `;
        });

        return resumeHtml;
    }

    getAllPrestations() {
        return [...(this.prestations.HOMME || []), ...(this.prestations.FEMME || [])];
    }

    getSelectedServicesNames(paire) {
        return paire.prestations.map(prestationId => {
            const prestation = this.getAllPrestations().find(p => p.id === prestationId);
            return prestation ? prestation.nom : '';
        }).filter(Boolean);
    }

    editerPaire(paireId) {
        const paire = this.paires.find(p => p.id === paireId);
        if (!paire) return;

        // Expand the pair for editing
        paire.validated = false;
        paire.collapsed = false;

        // Re-render to show full view
        this.renderAllPaires();
        this.updateValidationButton();
        this.saveToStorage(); // Save changes

        // Scroll to the pair
        setTimeout(() => {
            const paireElement = document.querySelector(`[data-paire-id="${paireId}"]`);
            if (paireElement) {
                paireElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }, 100);

        showToast('Paire en mode édition', 'info');
    }

    // localStorage management
    saveToStorage() {
        try {
            const data = {
                paires: this.paires,
                currentStep: this.currentStep,
                clientInfo: this.getClientInfo(),
                timestamp: Date.now()
            };
            localStorage.setItem(this.storageKey, JSON.stringify(data));
        } catch (error) {
            console.warn('Failed to save to localStorage:', error);
        }
    }

    loadFromStorage() {
        try {
            const savedData = localStorage.getItem(this.storageKey);
            if (savedData) {
                const data = JSON.parse(savedData);

                // Check if data is not too old (24 hours)
                const maxAge = 24 * 60 * 60 * 1000; // 24 hours in ms
                if (Date.now() - data.timestamp > maxAge) {
                    this.clearStorage();
                    this.ajouterPaire(); // Add first pair
                    return;
                }

                // Restore data
                this.paires = data.paires || [];
                this.currentStep = data.currentStep || 1;

                // Restore pairs
                if (this.paires.length > 0) {
                    this.renderAllPaires();
                    this.updateValidationButton();
                    this.allerEtape(this.currentStep);

                    // Restore client info if on payment step
                    if (this.currentStep === 3 && data.clientInfo) {
                        this.setClientInfo(data.clientInfo);
                    }

                    // Update recap if on validation step
                    if (this.currentStep === 2) {
                        this.renderRecapitulatif();
                    }

                    showToast('Commande restaurée', 'info');
                } else {
                    this.ajouterPaire(); // Add first pair if none saved
                }
            } else {
                this.ajouterPaire(); // Add first pair if no saved data
            }
        } catch (error) {
            console.warn('Failed to load from localStorage:', error);
            this.ajouterPaire(); // Add first pair on error
        }
    }

    getClientInfo() {
        if (!this.formCommande) return {};

        const formData = new FormData(this.formCommande);
        return {
            nom: formData.get('nom') || '',
            email: formData.get('email') || '',
            telephone: formData.get('telephone') || '',
            entreprise: formData.get('entreprise') || ''
        };
    }

    setClientInfo(clientInfo) {
        if (!this.formCommande || !clientInfo) return;

        const fields = ['nom', 'email', 'telephone', 'entreprise'];
        fields.forEach(field => {
            const input = this.formCommande.querySelector(`[name="${field}"]`);
            if (input && clientInfo[field]) {
                input.value = clientInfo[field];
            }
        });
    }

    clearStorage() {
        try {
            localStorage.removeItem(this.storageKey);
        } catch (error) {
            console.warn('Failed to clear localStorage:', error);
        }
    }

    allerEtape(etape) {
        // Hide all steps
        document.querySelectorAll('.etape').forEach(el => el.classList.remove('active'));
        document.querySelectorAll('.step').forEach(el => {
            el.classList.remove('active', 'completed');
        });

        // Show target step
        const targetEtape = document.getElementById(`etape-${['paires', 'validation', 'paiement'][etape - 1]}`);
        if (targetEtape) {
            targetEtape.classList.add('active');
        }

        // Update step indicator
        for (let i = 1; i <= 3; i++) {
            const step = document.getElementById(`step-${i}`);
            if (step) {
                if (i < etape) {
                    step.classList.add('completed');
                } else if (i === etape) {
                    step.classList.add('active');
                }
            }
        }

        this.currentStep = etape;
        this.saveToStorage(); // Save current step

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    validatePaymentForm() {
        const form = this.formCommande;
        if (!form) return;

        const isValid = validateForm(form);

        if (this.btnPayer) {
            this.btnPayer.disabled = !isValid;
        }
    }

    async traiterCommande(event) {
        event.preventDefault();

        if (!validateForm(this.formCommande)) {
            showToast('Veuillez remplir tous les champs requis', 'error');
            return;
        }

        try {
            showLoading();

            // Prepare order data
            const formData = new FormData(this.formCommande);
            const orderData = {
                nom: formData.get('nom'),
                email: formData.get('email'),
                telephone: formData.get('telephone'),
                entreprise: formData.get('entreprise'),
                paires: this.paires.map(paire => ({
                    type_chaussure: paire.type_chaussure,
                    photo_url: paire.photo_url,
                    photo_filename: paire.photo_filename,
                    description: paire.description,
                    prestations: paire.prestations
                }))
            };

            // Create order
            const orderResponse = await api.post('/commande', orderData);
            const commande = orderResponse.commande;

            // Create Stripe checkout session
            const checkoutResponse = await api.post(`/commande/${commande.id}/checkout`, {});

            // Clear saved data since order is being processed
            this.clearStorage();

            // Redirect to Stripe
            window.location.href = checkoutResponse.checkout_url;

        } catch (error) {
            console.error('Error processing order:', error);
            showToast('Erreur lors du traitement de la commande', 'error');
        } finally {
            hideLoading();
        }
    }
}

// Initialize order manager when DOM is loaded
let orderManager;

document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if we're on the order page
    if (document.getElementById('paires-container')) {
        orderManager = new OrderManager();

        // Make globally available
        window.orderManager = orderManager;
    }
});