import { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { CheckCircle2, Loader2, AlertCircle, Vote } from 'lucide-react';

export default function VotePage({ token }) {
    const [selectedCandidate, setSelectedCandidate] = useState(null);
    const [voteSubmitted, setVoteSubmitted] = useState(false);

    const { data: voteData, isLoading, error } = useQuery({
        queryKey: ['validateToken', token],
        queryFn: () => api.validateVotingToken(token),
        retry: false,
    });

    const voteMutation = useMutation({
        mutationFn: () => api.castVote(token, voteData.election.id, selectedCandidate),
        onSuccess: () => {
            setVoteSubmitted(true);
        },
        onError: (error) => {
            alert('❌ Failed to cast vote: ' + error.message);
        }
    });

    const handleVote = () => {
        if (!selectedCandidate) {
            alert('Please select a candidate');
            return;
        }
        if (confirm('Confirm your vote? This action cannot be undone.')) {
            voteMutation.mutate();
        }
    };

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-center">
                    <Loader2 className="w-12 h-12 animate-spin text-primary mx-auto mb-4" />
                    <p className="text-muted-foreground">Validating your voting link...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
                <Card className="max-w-md w-full">
                    <CardContent className="p-8 text-center">
                        <AlertCircle className="w-16 h-16 text-destructive mx-auto mb-4" />
                        <h2 className="text-2xl font-bold mb-2">Invalid Voting Link</h2>
                        <p className="text-muted-foreground">
                            {error.message || 'This voting link is invalid or has expired.'}
                        </p>
                    </CardContent>
                </Card>
            </div>
        );
    }

    if (voteSubmitted) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-blue-50 p-4">
                <Card className="max-w-md w-full">
                    <CardContent className="p-8 text-center">
                        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                            <CheckCircle2 className="w-10 h-10 text-green-600" />
                        </div>
                        <h2 className="text-2xl font-bold mb-2">Vote Submitted!</h2>
                        <p className="text-muted-foreground mb-6">
                            Thank you for participating in the election. Your vote has been recorded securely.
                        </p>
                        <div className="bg-blue-50 text-blue-800 p-4 rounded-lg text-sm">
                            <p className="font-medium mb-1">Election: {voteData?.election?.title}</p>
                            <p>Your vote is anonymous and cannot be changed.</p>
                        </div>
                    </CardContent>
                </Card>
            </div>
        );
    }

    const election = voteData?.election;

    return (
        <div className="min-h-screen bg-gradient-to-br from-primary/5 to-background p-4">
            <div className="max-w-3xl mx-auto py-8">
                {/* Header */}
                <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-primary rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <Vote className="w-10 h-10 text-white" />
                    </div>
                    <h1 className="text-3xl font-bold mb-2">{election?.title}</h1>
                    <Badge variant="active" className="mb-2">Active Election</Badge>
                    <p className="text-muted-foreground">
                        Select your preferred candidate and submit your vote
                    </p>
                </div>

                {/* Candidates */}
                <div className="space-y-4 mb-6">
                    {election?.candidates?.map((candidate) => (
                        <Card
                            key={candidate.id}
                            className={`cursor-pointer transition-all ${selectedCandidate === candidate.id
                                    ? 'border-primary border-2 bg-primary/5'
                                    : 'hover:border-primary/50'
                                }`}
                            onClick={() => setSelectedCandidate(candidate.id)}
                        >
                            <CardContent className="p-6">
                                <div className="flex items-start gap-4">
                                    <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${selectedCandidate === candidate.id
                                            ? 'border-primary bg-primary'
                                            : 'border-gray-300'
                                        }`}>
                                        {selectedCandidate === candidate.id && (
                                            <CheckCircle2 className="w-4 h-4 text-white" />
                                        )}
                                    </div>
                                    <div className="flex-1">
                                        <h3 className="text-xl font-semibold mb-1">{candidate.name}</h3>
                                        <Badge variant="outline" className="mb-2">{candidate.role}</Badge>
                                        {candidate.manifesto && (
                                            <p className="text-sm text-muted-foreground mt-2">
                                                {candidate.manifesto}
                                            </p>
                                        )}
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>

                {/* Submit Button */}
                <Card>
                    <CardContent className="p-6">
                        <Button
                            className="w-full"
                            size="lg"
                            onClick={handleVote}
                            disabled={!selectedCandidate || voteMutation.isPending}
                        >
                            {voteMutation.isPending ? (
                                <>
                                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                                    Submitting Vote...
                                </>
                            ) : (
                                <>
                                    <CheckCircle2 className="w-5 h-5 mr-2" />
                                    Submit Vote
                                </>
                            )}
                        </Button>
                        <p className="text-center text-sm text-muted-foreground mt-4">
                            🔒 Your vote is anonymous and secure
                        </p>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
