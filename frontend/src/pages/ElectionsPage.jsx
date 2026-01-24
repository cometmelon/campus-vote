import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import MainLayout from '@/components/MainLayout';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Plus, Calendar, Loader2, UserPlus, Trash2, Mail } from 'lucide-react';

export default function ElectionsPage() {
    const queryClient = useQueryClient();
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [formData, setFormData] = useState({
        title: '',
        department_id: '',
        status: 'planned',
        start_date: '',
        end_date: '',
        batch_size: 60,
        candidates: [],
    });
    const [newCandidate, setNewCandidate] = useState({ name: '', role: '', photo_url: '', manifesto: '' });

    const { data: elections, isLoading } = useQuery({
        queryKey: ['elections'],
        queryFn: () => api.getElections(),
    });

    const createMutation = useMutation({
        mutationFn: (data) => api.createElection(data),
        onSuccess: () => {
            queryClient.invalidateQueries(['elections']);
            setShowCreateModal(false);
            resetForm();
            alert('✅ Election created successfully!');
        },
        onError: (error) => {
            alert('❌ Error: ' + error.message);
        }
    });

    const updateStatusMutation = useMutation({
        mutationFn: ({ electionId, status }) => api.updateElectionStatus(electionId, status),
        onSuccess: () => {
            queryClient.invalidateQueries(['elections']);
        },
    });

    const sendLinksMutation = useMutation({
        mutationFn: ({ electionId }) => api.sendVotingLinks(electionId, null, 60),
        onSuccess: (data) => {
            alert(`✅ Voting links sent!\n\nTotal students: ${data.total_students}\nBatches: ${data.batches}`);
        },
    });

    const resetForm = () => {
        setFormData({
            title: '',
            department_id: '',
            status: 'planned',
            start_date: '',
            end_date: '',
            batch_size: 60,
            candidates: [],
        });
        setNewCandidate({ name: '', role: '', photo_url: '', manifesto: '' });
    };

    const handleAddCandidate = () => {
        if (!newCandidate.name || !newCandidate.role) {
            alert('Please enter both name and role');
            return;
        }
        setFormData(prev => ({
            ...prev,
            candidates: [...prev.candidates, { ...newCandidate }],
        }));
        setNewCandidate({ name: '', role: '', photo_url: '', manifesto: '' });
    };

    const handleRemoveCandidate = (index) => {
        setFormData(prev => ({
            ...prev,
            candidates: prev.candidates.filter((_, i) => i !== index),
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (formData.candidates.length === 0) {
            alert('Please add at least one candidate');
            return;
        }
        const data = {
            ...formData,
            department_id: formData.department_id === 'all' ? null : formData.department_id || null,
            start_date: new Date(formData.start_date).toISOString(),
            end_date: new Date(formData.end_date).toISOString(),
        };
        createMutation.mutate(data);
    };

    const formatDate = (dateStr) => {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    };

    return (
        <MainLayout>
            <div className="space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">Election Management</h1>
                        <p className="text-gray-600 mt-1">Create, manage, and monitor departmental elections.</p>
                    </div>
                    <Button onClick={() => setShowCreateModal(true)} className="gap-2">
                        <Plus className="w-4 h-4" />
                        Create Election
                    </Button>
                </div>

                {/* Elections Table */}
                <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
                    <table className="w-full">
                        <thead className="bg-gray-50 border-b border-gray-200">
                            <tr>
                                <th className="text-left px-6 py-3 text-xs font-medium text-gray-600 uppercase tracking-wider">Election Title</th>
                                <th className="text-left px-6 py-3 text-xs font-medium text-gray-600 uppercase tracking-wider">Department</th>
                                <th className="text-left px-6 py-3 text-xs font-medium text-gray-600 uppercase tracking-wider">Status</th>
                                <th className="text-left px-6 py-3 text-xs font-medium text-gray-600 uppercase tracking-wider">Timeline</th>
                                <th className="text-right px-6 py-3 text-xs font-medium text-gray-600 uppercase tracking-wider">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {isLoading ? (
                                <tr>
                                    <td colSpan={5} className="px-6 py-12 text-center">
                                        <Loader2 className="w-6 h-6 animate-spin mx-auto text-gray-400" />
                                    </td>
                                </tr>
                            ) : elections?.length === 0 ? (
                                <tr>
                                    <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                                        No elections found. Create one to get started.
                                    </td>
                                </tr>
                            ) : (
                                elections?.map((election) => (
                                    <tr key={election.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4">
                                            <p className="font-medium text-gray-900">{election.title}</p>
                                        </td>
                                        <td className="px-6 py-4">
                                            <Badge variant="outline" className="bg-gray-100 text-gray-700 border-0">
                                                {election.department?.code || 'All'}
                                            </Badge>
                                        </td>
                                        <td className="px-6 py-4">
                                            <Badge
                                                className={
                                                    election.status === 'planned' ? 'bg-yellow-100 text-yellow-800' :
                                                        election.status === 'active' ? 'bg-green-100 text-green-800' :
                                                            'bg-gray-100 text-gray-800'
                                                }
                                            >
                                                {election.status.charAt(0).toUpperCase() + election.status.slice(1)}
                                            </Badge>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-2 text-sm text-gray-600">
                                                <Calendar className="w-4 h-4" />
                                                {formatDate(election.start_date)} - {formatDate(election.end_date)}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            {election.status === 'planned' && (
                                                <Button
                                                    variant="outline"
                                                    size="sm"
                                                    onClick={() => updateStatusMutation.mutate({ electionId: election.id, status: 'active' })}
                                                >
                                                    Activate
                                                </Button>
                                            )}
                                            {election.status === 'active' && (
                                                <Button
                                                    size="sm"
                                                    onClick={() => sendLinksMutation.mutate({ electionId: election.id })}
                                                    className="gap-2"
                                                >
                                                    <Mail className="w-4 h-4" />
                                                    Notify Voters
                                                </Button>
                                            )}
                                            {election.status === 'finished' && (
                                                <span className="text-sm text-gray-500">Finished</span>
                                            )}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Create Election Modal */}
                <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
                    <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                        <DialogHeader>
                            <DialogTitle>Create New Election</DialogTitle>
                            <DialogDescription>
                                Set up a new departmental or general election with candidates.
                            </DialogDescription>
                        </DialogHeader>

                        <form onSubmit={handleSubmit} className="space-y-5">
                            <div className="space-y-2">
                                <Label htmlFor="title">Election Title</Label>
                                <Input
                                    id="title"
                                    placeholder="e.g. Student Council President 2024"
                                    value={formData.title}
                                    onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                                    required
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label>Department</Label>
                                    <Select
                                        value={formData.department_id || 'all'}
                                        onValueChange={(value) => setFormData(prev => ({ ...prev, department_id: value }))}
                                    >
                                        <SelectTrigger>
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="all">All Departments</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                                <div className="space-y-2">
                                    <Label>Initial Status</Label>
                                    <Select
                                        value={formData.status}
                                        onValueChange={(value) => setFormData(prev => ({ ...prev, status: value }))}
                                    >
                                        <SelectTrigger>
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="planned">Planned</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label htmlFor="start_date">Start Date</Label>
                                    <Input
                                        id="start_date"
                                        type="datetime-local"
                                        value={formData.start_date}
                                        onChange={(e) => setFormData(prev => ({ ...prev, start_date: e.target.value }))}
                                        required
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="end_date">End Date</Label>
                                    <Input
                                        id="end_date"
                                        type="datetime-local"
                                        value={formData.end_date}
                                        onChange={(e) => setFormData(prev => ({ ...prev, end_date: e.target.value }))}
                                        required
                                    />
                                </div>
                            </div>

                            {/* Candidates Section */}
                            <div className="space-y-3 border-t pt-4">
                                <div className="flex items-center justify-between">
                                    <Label className="text-base">Candidates</Label>
                                    <Button type="button" variant="outline" size="sm" onClick={handleAddCandidate}>
                                        <Plus className="w-4 h-4 mr-1" />
                                        Add Candidate
                                    </Button>
                                </div>

                                {formData.candidates.length > 0 && (
                                    <div className="space-y-2">
                                        {formData.candidates.map((candidate, index) => (
                                            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                                <div>
                                                    <p className="font-medium text-sm">{candidate.name}</p>
                                                    <p className="text-xs text-gray-600">Role: {candidate.role}</p>
                                                </div>
                                                <Button
                                                    type="button"
                                                    variant="ghost"
                                                    size="sm"
                                                    onClick={() => handleRemoveCandidate(index)}
                                                >
                                                    <Trash2 className="w-4 h-4 text-red-500" />
                                                </Button>
                                            </div>
                                        ))}
                                    </div>
                                )}

                                <div className="grid grid-cols-2 gap-3 p-3 bg-gray-50 rounded-lg">
                                    <Input
                                        placeholder="Candidate Name"
                                        value={newCandidate.name}
                                        onChange={(e) => setNewCandidate(prev => ({ ...prev, name: e.target.value }))}
                                    />
                                    <Input
                                        placeholder="e.g. President"
                                        value={newCandidate.role}
                                        onChange={(e) => setNewCandidate(prev => ({ ...prev, role: e.target.value }))}
                                    />
                                    <Input
                                        placeholder="Photo URL (optional)"
                                        value={newCandidate.photo_url}
                                        onChange={(e) => setNewCandidate(prev => ({ ...prev, photo_url: e.target.value }))}
                                        className="col-span-2"
                                    />
                                    <Input
                                        placeholder="Short manifesto..."
                                        value={newCandidate.manifesto}
                                        onChange={(e) => setNewCandidate(prev => ({ ...prev, manifesto: e.target.value }))}
                                        className="col-span-2"
                                    />
                                </div>
                            </div>

                            <div className="flex justify-end gap-3 pt-4">
                                <Button type="button" variant="outline" onClick={() => setShowCreateModal(false)}>
                                    Cancel
                                </Button>
                                <Button type="submit" disabled={createMutation.isPending}>
                                    {createMutation.isPending ? (
                                        <>
                                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                            Creating...
                                        </>
                                    ) : (
                                        'Create Election'
                                    )}
                                </Button>
                            </div>
                        </form>
                    </DialogContent>
                </Dialog>
            </div>
        </MainLayout>
    );
}
