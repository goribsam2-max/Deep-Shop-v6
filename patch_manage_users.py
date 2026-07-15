import re

with open('pages/admin/ManageUsers.tsx', 'r') as f:
    content = f.read()

# Add states for managing reviews
state_match = "const [deletingUserId, setDeletingUserId] = useState<string | null>(null);"
state_replace = """const [deletingUserId, setDeletingUserId] = useState<string | null>(null);
  const [showReviewsModal, setShowReviewsModal] = useState<string | null>(null);
  const [userReviews, setUserReviews] = useState<any[]>([]);
  const [editingReview, setEditingReview] = useState<any>(null);
  const [newReview, setNewReview] = useState({ rating: 5, comment: "" });"""
content = content.replace(state_match, state_replace)

# Add function to load reviews
func_match = """  const filteredUsers = users.filter((u) => {"""
func_replace = """
  const loadUserReviews = async (userId: string) => {
    setShowReviewsModal(userId);
    const userDoc = users.find(u => u.id === userId);
    setUserReviews(userDoc?.reviews || []);
  };

  const handleSaveReview = async () => {
    if(!showReviewsModal) return;
    try {
      const userRef = doc(db, 'users', showReviewsModal);
      let updatedReviews = [...userReviews];
      
      if(editingReview) {
        updatedReviews = updatedReviews.map(r => r.createdAt === editingReview.createdAt ? { ...r, rating: newReview.rating, comment: newReview.comment } : r);
      } else {
        updatedReviews.unshift({
           reviewerId: "admin",
           reviewerName: "Admin",
           rating: newReview.rating,
           comment: newReview.comment,
           createdAt: Date.now()
        });
      }
      
      await updateDoc(userRef, { reviews: updatedReviews });
      setUserReviews(updatedReviews);
      
      // Update local state
      setUsers(users.map(u => u.id === showReviewsModal ? { ...u, reviews: updatedReviews } : u));
      setEditingReview(null);
      setNewReview({ rating: 5, comment: "" });
      notify("Review saved successfully", "success");
    } catch(e) {
      notify("Failed to save review", "error");
    }
  };

  const handleDeleteReview = async (createdAt: number) => {
    if(!showReviewsModal) return;
    if(window.confirm("Delete this review?")) {
        try {
            const userRef = doc(db, 'users', showReviewsModal);
            const updatedReviews = userReviews.filter(r => r.createdAt !== createdAt);
            await updateDoc(userRef, { reviews: updatedReviews });
            setUserReviews(updatedReviews);
            setUsers(users.map(u => u.id === showReviewsModal ? { ...u, reviews: updatedReviews } : u));
            notify("Review deleted", "success");
        } catch(e) {
            notify("Failed to delete review", "error");
        }
    }
  };

  const filteredUsers = users.filter((u) => {"""
content = content.replace(func_match, func_replace)

# Add Manage Reviews button to user dropdown
menu_match = """                              <button
                                onClick={() =>
                                  setUserToEditLevel(user.id)
                                }
                                className="w-full flex items-center gap-2 px-4 py-2 text-sm text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800"
                              >
                                <Icon name="shield" className="w-4 h-4" />
                                Edit Auth Level
                              </button>"""
menu_replace = """                              <button
                                onClick={() =>
                                  setUserToEditLevel(user.id)
                                }
                                className="w-full flex items-center gap-2 px-4 py-2 text-sm text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800"
                              >
                                <Icon name="shield" className="w-4 h-4" />
                                Edit Auth Level
                              </button>
                              <button
                                onClick={() => {
                                  loadUserReviews(user.id);
                                  setActiveMenu(null);
                                }}
                                className="w-full flex items-center gap-2 px-4 py-2 text-sm text-emerald-600 dark:text-emerald-400 hover:bg-zinc-100 dark:hover:bg-zinc-800"
                              >
                                <Icon name="star" className="w-4 h-4" />
                                Manage Trust Reviews
                              </button>"""
content = content.replace(menu_match, menu_replace)

# Render the modal at the bottom
modal_match = """      </AnimatePresence>
    </div>
  );
};"""
modal_replace = """      </AnimatePresence>
      
      {/* Reviews Modal */}
      <AnimatePresence>
        {showReviewsModal && (
          <div className="fixed inset-0 z-[1000] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white dark:bg-zinc-900 rounded-3xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-xl"
            >
              <h2 className="text-xl font-bold mb-4 text-zinc-900 dark:text-white">Manage User Trust Reviews</h2>
              
              <div className="bg-zinc-50 dark:bg-zinc-800 p-4 rounded-xl mb-6">
                 <h3 className="text-sm font-semibold mb-2">{editingReview ? "Edit Review" : "Add New Review"}</h3>
                 <div className="flex gap-2 mb-2">
                    {[1,2,3,4,5].map(s => (
                        <button key={s} onClick={() => setNewReview({...newReview, rating: s})} className={`text-xl ${newReview.rating >= s ? 'text-amber-500' : 'text-zinc-300'}`}>★</button>
                    ))}
                 </div>
                 <textarea 
                    value={newReview.comment} 
                    onChange={e => setNewReview({...newReview, comment: e.target.value})} 
                    className="w-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 rounded-lg p-2 text-sm mb-2"
                    placeholder="Review comment..."
                 />
                 <div className="flex gap-2">
                     <button onClick={handleSaveReview} className="px-4 py-2 bg-emerald-500 text-white rounded-lg text-sm font-medium">Save Review</button>
                     {editingReview && (
                         <button onClick={() => { setEditingReview(null); setNewReview({ rating: 5, comment: "" }); }} className="px-4 py-2 bg-zinc-200 text-zinc-900 rounded-lg text-sm font-medium">Cancel Edit</button>
                     )}
                 </div>
              </div>

              <div className="space-y-3">
                 {userReviews.length === 0 && <p className="text-sm text-zinc-500">No reviews yet.</p>}
                 {userReviews.map((r, i) => (
                    <div key={i} className="border border-zinc-200 dark:border-zinc-700 rounded-xl p-3 flex justify-between items-start">
                        <div>
                            <div className="flex items-center gap-2 mb-1">
                                <span className="font-bold text-sm text-zinc-900 dark:text-white">{r.reviewerName || 'Anonymous'}</span>
                                <span className="text-amber-500 text-xs">{"★".repeat(r.rating)}{"☆".repeat(5-r.rating)}</span>
                            </div>
                            <p className="text-sm text-zinc-600 dark:text-zinc-400">{r.comment}</p>
                        </div>
                        <div className="flex gap-2 shrink-0">
                            <button onClick={() => { setEditingReview(r); setNewReview({ rating: r.rating, comment: r.comment }); }} className="p-1.5 bg-blue-100 text-blue-600 rounded-lg"><Icon name="edit" className="w-3 h-3"/></button>
                            <button onClick={() => handleDeleteReview(r.createdAt)} className="p-1.5 bg-red-100 text-red-600 rounded-lg"><Icon name="trash" className="w-3 h-3"/></button>
                        </div>
                    </div>
                 ))}
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  onClick={() => setShowReviewsModal(null)}
                  className="px-6 py-2 bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-white rounded-xl font-medium"
                >
                  Close
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};"""
content = content.replace(modal_match, modal_replace)

with open('pages/admin/ManageUsers.tsx', 'w') as f:
    f.write(content)

print("Manage users patched")
