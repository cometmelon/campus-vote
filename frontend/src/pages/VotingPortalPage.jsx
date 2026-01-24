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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Send, Users, Eye, StopCircle, Loader2, Mail } from 'lucide-react';

export default function VotingPortalPage() {
    const { isAdmin } = useAuth();
    const queryClient = useQueryClient();
    const [selectedElection, setSelectedElection] = useState('');
    const [batchSize, setBatchSize] = useState('100');

    const { data: elections } = useQuery({
        queryKey: ['elections'],
        queryFn: () => api.getElections(),
    });

    const { data: activeElections, isLoading: activeLoading } = useQuery({
        queryKey: ['activeElections'],
        queryFn: () => api.getActiveElections(),
        enabled: !isAdmin,
    });

    const sendLinksMutation = useMutation({
        mutationFn: ({ electionId, batchSize }) => {
            return api.sendVotingLinks(electionId, null, parseInt(batchSize));
        },
        onSuccess: (data) => {
            alert(`✅ ${data.message}\n\nTotal: ${data.total_students} students`);
            queryClient.invalidateQueries(['elections']);
        },
        onError: (error) => {
            alert('❌ Failed: ' + error.message);
        },
    });

    const updateStatusMutation = useMutation({
        mutationFn: ({ electionId, status }) => {
            return api.updateElectionStatus(electionId, status);
        },
        onSuccess: () => {
            queryClient.invalidateQueries(['elections']);
            alert('✅ Election ended successfully');
        },
        onError: (error) => {
            alert('❌ Failed: ' + error.message);
        },
    });

    const activeElectionsList = elections?.filter(e => e.status === 'active') || [];

    const handleSendLinks = () => {
        if (!selectedElection) {
            alert('Please select an election first');
            return;
        }
        sendLinksMutation.mutate({
            electionId: selectedElection,
            batchSize: batchSize,
        });
    };

    const handleEndElection = (electionId) => {
        updateStatusMutation.mutate({ electionId, status: 'finished' });
    };

    // Admin View
    if (isAdmin) {
        return (
            <MainLayout>
                <div className="space-y-6">
                    {/* Header */}
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">Voting Portal</h1>
                        <p className="text-gray-600 mt-1">Manage voting links and monitor active elections.</p>
                    </div>

                    {/* Send Voting Links Card */}
                    <Card className="border-0 shadow-sm">
                        <CardContent className="p-6">
                            <div className="flex items-start gap-3 mb-5">
                                <div className="w-10 h-10 rounded-lg bg-indigo-50 flex items-center justify-center">
                                    <Send className="w-5 h-5 text-indigo-600" />
                                </div>
                                <div>
                                    <h3 className="font-semibold text-gray-900">Send Voting Links</h3>
                                    <p className="text-sm text-gray-600">Send voting links to department students with load balancing support.</p>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
                                <div className="space-y-2">
                                    <Label className="text-sm font-medium">Target Department</Label>
                                    <Select value={selectedElection} onValueChange={setSelectedElection}>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select department" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {activeElectionsList.length === 0 ? (
                                                <SelectItem value="none" disabled>No active elections</SelectItem>
                                            ) : (
                                                activeElectionsList.map(election => (
                                                    <SelectItem key={election.id} value={election.id}>
                                                        {election.title}
                                                    </SelectItem>
                                                ))
                                            )}
                                        </SelectContent>
                                    </Select>
                                </div>
                                <div className="space-y-2">
                                    <Label className="text-sm font-medium">Batch Size (Load Balancing)</Label>
                                    <Input
                                        type="number"
                                        value={batchSize}
                                        onChange={(e) => setBatchSize(e.target.value)}
                                        min="10"
                                        max="500"
                                    />
                                </div>
                                <div>
                                    <Button
                                        className="w-full gap-2"
                                        onClick={handleSendLinks}
                                        disabled={!selectedElection || sendLinksMutation.isPending}
                                    >
                                        {sendLinksMutation.isPending ? (
                                            <>
                                                <Loader2 className="w-4 h-4 animate-spin" />
                                                Sending...
                                            </>
                                        ) : (
                                            <>
                                                <Mail className="w-4 h-4" />
                                                Send Voting Links
                                            </>
                                        )}
                                    </Button>
                                </div>
                            </div>

                            <p className="text-xs text-gray-500 mt-4 bg-blue-50 p-3 rounded-lg">
                                <strong>Load Balancing:</strong> Emails will be sent in batches to prevent server overload. Each batch will be sent with a 5-second delay to ensure reliable delivery to all students.
                            </p>
                        </CardContent>
                    </Card>

                    {/* Active Elections */}
                    <div>
                        <h2 className="text-xl font-semibold text-gray-900 mb-4">Active Elections</h2>
                        {activeElectionsList.length === 0 ? (
                            <Card className="border-0 shadow-sm">
                                <CardContent className="py-12 text-center text-gray-500">
                                    <Mail className="w-12 h-12 mx-auto mb-4 opacity-50" />
                                    <p>No active elections at the moment.</p>
                                    <p className="text-sm">Activate an election from the Elections page.</p>
                                </CardContent>
                            </Card>
                        ) : (
                            <div className="space-y-4">
                                {activeElectionsList.map((election) => (
                                    <Card key={election.id} className="border-0 shadow-sm">
                                        <CardContent className="p-6">
                                            <div className="flex items-start justify-between mb-4">
                                                <div>
                                                    <div className="flex items-center gap-3 mb-2">
                                                        <h3 className="font-semibold text-gray-900 text-lg">{election.title}</h3>
                                                        <Badge className="bg-green-100 text-green-800">Active</Badge>
                                                    </div>
                                                    <p className="text-sm text-gray-600">{election.department?.code || 'ECE'}</p>
                                                    <div className="flex items-center gap-4 mt-3">
                                                        <div className="text-sm">
                                                            <p className="text-gray-500">Ends: {new Date(election.end_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })}</p>
                                                        </div>
                                                        <div className="flex items-center gap-2 text-sm">
                                                            <Users className="w-4 h-4 text-gray-500" />
                                                            <span className="text-gray-700 font-medium">Participation</span>
                                                            <span className="text-gray-900 font-semibold">0%</span>
                                                        </div>
                                                    </div>
                                                    <p className="text-xs text-gray-500 mt-2">0 of 450 eligible voters</p>
                                                </div>
                                            </div>

                                            <div className="flex gap-3">
                                                <Button variant="outline" className="flex-1 gap-2">
                                                    <Eye className="w-4 h-4" />
                                                    View Votes
                                                </Button>
                                                <Button
                                                    variant="outline"
                                                    className="flex-1 gap-2 text-red-600 border-red-200 hover:bg-red-50"
                                                    onClick={() => handleEndElection(election.id)}
                                                    disabled={updateStatusMutation.isPending}
                                                >
                                                    {updateStatusMutation.isPending ? (
                                                        <>
                                                            <Loader2 className="w-4 h-4 animate-spin" />
                                                            Ending...
                                                        </>
                                                    ) : (
                                                        <>
                                                            <StopCircle className="w-4 h-4" />
                                                            End Election
                                                        </>
                                                    )}
                                                </Button>
                                            </div>
                                        </CardContent>
                                    </Card>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </MainLayout>
        );
    }

    // Student View
    return (
        <MainLayout>
            <div className="max-w-3xl mx-auto">
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold text-gray-900 mb-2">Student Voting Portal</h1>
                    <p className="text-gray-600">
                        Participate in active elections. Your vote matters in shaping the future of our campus community.
                    </p>
                </div>

                {activeLoading ? (
                    <div className="flex items-center justify-center py-12">
                        <Loader2 className="w-8 h-8 animate-spin text-primary" />
                    </div>
                ) : !activeElections || activeElections.length === 0 ? (
                    <Card className="border-0 shadow-sm">
                        <CardContent className="py-16 text-center">
                            <Mail className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                            <h3 className="font-semibold text-lg mb-2 text-gray-900">No Active Elections</h3>
                            <p className="text-gray-600 mb-6">
                                No active elections for your department right now.
                            </p>
                        </CardContent>
                    </Card>
                ) : (
                    <div className="space-y-4">
                        {activeElections.map((election) => (
                            <Card key={election.id} className="border-2 border-indigo-100 shadow-sm hover:shadow-md transition-shadow">
                                <CardContent className="p-6">
                                    <div className="flex items-start justify-between mb-4">
                                        <Badge className="bg-indigo-100 text-indigo-700 border-0">
                                            {election.department?.code || 'ECE'}
                                        </Badge>
                                        <p className="text-sm text-gray-500">
                                            Ends {new Date(election.end_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                                        </p>
                                    </div>
                                    <h3 className="text-xl font-bold text-gray-900 mb-2">{election.title}</h3>
                                    <p className="text-sm text-gray-600 mb-6">
                                        Select a candidate to view their manifesto and cast your vote.
                                    </p>
                                    <Button className="w-full">
                                        Proceed to Vote
                                    </Button>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                )}
            </div>
        </MainLayout>
    );
}
