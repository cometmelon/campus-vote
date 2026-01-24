import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import MainLayout from '@/components/MainLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Users, Loader2, Plus, Trash2 } from 'lucide-react';

export default function ClubsPage() {
    const { isAdmin } = useAuth();
    const queryClient = useQueryClient();
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [formData, setFormData] = useState({ name: '', category: '', description: '' });

    const { data: clubs, isLoading } = useQuery({
        queryKey: ['clubs'],
        queryFn: () => api.getClubs(),
    });

    const createMutation = useMutation({
        mutationFn: (data) => api.createClub(data),
        onSuccess: () => {
            queryClient.invalidateQueries(['clubs']);
            setShowCreateModal(false);
            setFormData({ name: '', category: '', description: '' });
            alert('✅ Club created successfully!');
        },
        onError: (error) => {
            alert('❌ Failed: ' + error.message);
        }
    });

    const deleteMutation = useMutation({
        mutationFn: (id) => api.deleteClub(id),
        onSuccess: () => {
            queryClient.invalidateQueries(['clubs']);
            alert('✅ Club deleted');
        },
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        createMutation.mutate(formData);
    };

    return (
        <MainLayout>
            <div className="space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">Clubs & Communities</h1>
                        <p className="text-gray-600 mt-1">Discover and join vibrant student communities.</p>
                    </div>
                    {isAdmin && (
                        <Button onClick={() => setShowCreateModal(true)} className="gap-2">
                            <Plus className="w-4 h-4" />
                            Add Club
                        </Button>
                    )}
                </div>

                {isLoading ? (
                    <div className="flex items-center justify-center py-12">
                        <Loader2 className="w-8 h-8 animate-spin text-primary" />
                    </div>
                ) : clubs?.length === 0 ? (
                    <Card className="border-0 shadow-sm">
                        <CardContent className="py-12 text-center text-gray-500">
                            No clubs registered yet.
                        </CardContent>
                    </Card>
                ) : (
                    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                        {clubs?.map((club) => (
                            <Card key={club.id} className="border-0 shadow-sm hover:shadow-md transition-shadow">
                                <CardContent className="p-6">
                                    {club.category && (
                                        <Badge className="bg-green-100 text-green-700 border-0 mb-4">
                                            {club.category.toUpperCase()}
                                        </Badge>
                                    )}

                                    <h3 className="text-xl font-bold text-gray-900 mb-2">{club.name}</h3>

                                    {club.description && (
                                        <p className="text-sm text-gray-600 mb-4">
                                            {club.description}
                                        </p>
                                    )}

                                    <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
                                        <Users className="w-4 h-4" />
                                        <span>{club.member_count || 1} Members</span>
                                    </div>

                                    <div className="flex gap-2">
                                        <Button variant="link" className="p-0 h-auto text-indigo-600 hover:text-indigo-700">
                                            View Roster
                                        </Button>
                                        {isAdmin && (
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                className="ml-auto text-red-600 hover:text-red-700 hover:bg-red-50"
                                                onClick={() => {
                                                    if (confirm(`Delete "${club.name}"?`)) {
                                                        deleteMutation.mutate(club.id);
                                                    }
                                                }}
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </Button>
                                        )}
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                )}

                {/* Create Club Modal */}
                <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Add New Club</DialogTitle>
                        </DialogHeader>

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="name">Club Name</Label>
                                <Input
                                    id="name"
                                    placeholder="e.g. Space Club"
                                    value={formData.name}
                                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                                    required
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="category">Category</Label>
                                <Input
                                    id="category"
                                    placeholder="e.g. tech club"
                                    value={formData.category}
                                    onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="description">Description</Label>
                                <Input
                                    id="description"
                                    placeholder="Brief description"
                                    value={formData.description}
                                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                                />
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
                                        'Create Club'
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
