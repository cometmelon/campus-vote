/**
 * API client for CampusVote backend
 */

const API_BASE = 'http://localhost:8000';

class ApiClient {
    constructor() {
        this.tokenKey = 'campusvote_token';
    }

    getToken() {
        return localStorage.getItem(this.tokenKey);
    }

    setToken(token) {
        localStorage.setItem(this.tokenKey, token);
    }

    clearToken() {
        localStorage.removeItem(this.tokenKey);
    }

    async request(endpoint, options = {}) {
        const token = this.getToken();
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(`${API_BASE}${endpoint}`, {
                ...options,
                headers,
            });

            if (response.status === 401) {
                this.clearToken();
                throw new Error('Session expired. Please login again.');
            }

            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.detail || `Request failed: ${response.status}`);
            }

            return response.json();
        } catch (error) {
            if (error.message === 'Failed to fetch') {
                throw new Error('Cannot connect to server. Please check if the backend is running.');
            }
            throw error;
        }
    }

    // Auth
    async login(studentId, password) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ student_id: studentId, password }),
        });
        this.setToken(data.access_token);
        return data;
    }

    async getMe() {
        return this.request('/auth/me');
    }

    logout() {
        this.clearToken();
    }

    // Elections
    async getElections(status = null) {
        const params = status ? `?status=${status}` : '';
        return this.request(`/elections${params}`);
    }

    async getElection(id) {
        return this.request(`/elections/${id}`);
    }

    async createElection(data) {
        return this.request('/elections', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async updateElectionStatus(id, status) {
        return this.request(`/elections/${id}/status?new_status=${status}`, {
            method: 'PUT',
        });
    }

    async deleteElection(id) {
        return this.request(`/elections/${id}`, { method: 'DELETE' });
    }

    // Voting
    async sendVotingLinks(electionId, departmentId, batchSize) {
        return this.request('/voting/send-links', {
            method: 'POST',
            body: JSON.stringify({
                election_id: electionId,
                department_id: departmentId,
                batch_size: batchSize,
            }),
        });
    }

    async validateVotingToken(token) {
        return this.request(`/voting/validate/${token}`);
    }

    async castVote(token, electionId, candidateId) {
        return this.request(`/voting/cast/${token}`, {
            method: 'POST',
            body: JSON.stringify({
                election_id: electionId,
                candidate_id: candidateId,
            }),
        });
    }

    async getActiveElections() {
        return this.request('/voting/active');
    }

    // Clubs
    async getClubs() {
        return this.request('/clubs');
    }

    async getClub(id) {
        return this.request(`/clubs/${id}`);
    }

    async createClub(data) {
        return this.request('/clubs', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async deleteClub(id) {
        return this.request(`/clubs/${id}`, { method: 'DELETE' });
    }

    // Dashboard
    async getDashboardStats() {
        return this.request('/dashboard/stats');
    }

    async getDepartmentTurnout() {
        return this.request('/dashboard/turnout');
    }

    async getRecentElections() {
        return this.request('/dashboard/recent-elections');
    }
}

export const api = new ApiClient();
