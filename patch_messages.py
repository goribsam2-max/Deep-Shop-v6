import re
import sys

with open('pages/Messages.tsx', 'r') as f:
    content = f.read()

# 1. Add currentPinnedIndex state
content = content.replace("const [callType, setCallType] = useState<'audio' | 'video'>('audio');", "const [callType, setCallType] = useState<'audio' | 'video'>('audio');\n  const [currentPinnedIndex, setCurrentPinnedIndex] = useState(0);")

# 2. Update handlePinMessage
new_handlePinMessage = """
  const handlePinMessage = async (msg: any) => {
    if (!channelIdParam) return;
    try {
      const channel = communityChannels.find(c => c.id === channelIdParam);
      let currentPins = channel?.pinnedMessages || [];
      if (channel?.pinnedMessage && !currentPins.some((p: any) => p.id === channel.pinnedMessage.id)) {
        currentPins.unshift(channel.pinnedMessage);
      }
      
      const newPin = {
        id: msg.id,
        text: msg.text || "Image Attachment",
        imageUrl: msg.imageUrl || ""
      };
      
      // Remove if already pinned, else add to front
      currentPins = currentPins.filter((p: any) => p.id !== msg.id);
      currentPins.unshift(newPin);
      
      await updateDoc(doc(db, 'community_channels', channelIdParam), {
        pinnedMessages: currentPins,
        pinnedMessage: null
      });
      notify("Message pinned successfully!", "success");
    } catch (err) {
      console.error(err);
      notify("Failed to pin message", "error");
    }
  };
"""
content = re.sub(r'const handlePinMessage = async \(msg: any\) => \{[\s\S]*?notify\("Failed to pin message", "error"\);\n    \}\n  \};', new_handlePinMessage.strip(), content)

# 3. Update handleUnpinMessage to use current channel pin
new_handleUnpinMessage = """
  const handleUnpinMessage = async (msgIdToUnpin?: string) => {
    if (!channelIdParam) return;
    try {
      const channel = communityChannels.find(c => c.id === channelIdParam);
      let currentPins = channel?.pinnedMessages || [];
      if (channel?.pinnedMessage && !currentPins.some((p: any) => p.id === channel.pinnedMessage.id)) {
        currentPins.unshift(channel.pinnedMessage);
      }
      
      if (msgIdToUnpin) {
          currentPins = currentPins.filter((p: any) => p.id !== msgIdToUnpin);
      } else {
          // Unpin current if none provided
          const currentPin = currentPins[currentPinnedIndex % currentPins.length];
          if (currentPin) {
              currentPins = currentPins.filter((p: any) => p.id !== currentPin.id);
          }
      }
      
      await updateDoc(doc(db, 'community_channels', channelIdParam), {
        pinnedMessages: currentPins,
        pinnedMessage: null
      });
      setCurrentPinnedIndex(0);
      notify("Message unpinned", "info");
    } catch (err) {
      console.error(err);
      notify("Failed to unpin message", "error");
    }
  };
"""
content = re.sub(r'const handleUnpinMessage = async \(\) => \{[\s\S]*?notify\("Failed to unpin message", "error"\);\n    \}\n  \};', new_handleUnpinMessage.strip(), content)

# 4. Render pinned messages in channel
old_channel_pin_render = """
                  {activeChannel.pinnedMessage && (
                    <div className="bg-gradient-to-r from-amber-50 to-orange-50 dark:from-zinc-900/90 dark:to-zinc-950/90 border-b border-amber-100 dark:border-zinc-800 px-4 py-2 flex items-center justify-between text-xs shrink-0 z-10 shadow-sm relative">
                      <div className="flex items-center gap-2 min-w-0 cursor-pointer flex-1" onClick={() => {
                        const targetMsg = channelMessages.find(m => m.id === activeChannel.pinnedMessage.id);
                        if (targetMsg) {
                          document.getElementById(`msg-${targetMsg.id}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                          triggerHighlight(targetMsg.id);
                        } else {
                          notify(`Pinned: ${activeChannel.pinnedMessage.text}`, "info");
                        }
                      }}>
                        <Pin className="w-3.5 h-3.5 text-[#EF8020] rotate-45 shrink-0" />
                        <div className="min-w-0">
                          <p className="font-bold text-[10px] text-[#EF8020] uppercase tracking-wider">Pinned Message</p>
                          <p className="text-[11px] text-zinc-600 dark:text-zinc-300 truncate mt-0.5">{activeChannel.pinnedMessage.text}</p>
                        </div>
                      </div>
                      {activeChannel.creatorId === user.uid && (
                        <button 
                          type="button" 
                          onClick={handleUnpinMessage}
                          className="p-1 rounded-full bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 text-zinc-400 hover:text-zinc-600 transition ml-2"
                          title="Unpin Message"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      )}
                    </div>
                  )}
"""

new_channel_pin_render = """
                  {(() => {
                    const pins = activeChannel?.pinnedMessages || (activeChannel?.pinnedMessage ? [activeChannel.pinnedMessage] : []);
                    if (pins.length === 0) return null;
                    const currentPin = pins[currentPinnedIndex % pins.length];
                    return (
                    <div className="bg-gradient-to-r from-amber-50 to-orange-50 dark:from-zinc-900/90 dark:to-zinc-950/90 border-b border-amber-100 dark:border-zinc-800 px-4 py-2 flex items-center justify-between text-xs shrink-0 z-10 shadow-sm relative">
                      <div className="flex items-center gap-2 min-w-0 cursor-pointer flex-1" onClick={() => {
                        const targetMsg = channelMessages.find(m => m.id === currentPin.id);
                        if (targetMsg) {
                          document.getElementById(`msg-${targetMsg.id}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                          triggerHighlight(targetMsg.id);
                        } else {
                          notify(`Pinned: ${currentPin.text}`, "info");
                        }
                        if (pins.length > 1) {
                            setCurrentPinnedIndex(prev => prev + 1);
                        }
                      }}>
                        <Pin className="w-3.5 h-3.5 text-[#EF8020] rotate-45 shrink-0" />
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                              <p className="font-bold text-[10px] text-[#EF8020] uppercase tracking-wider">Pinned Message {pins.length > 1 ? `(${ (currentPinnedIndex % pins.length) + 1 }/${pins.length})` : ""}</p>
                              {pins.length > 1 && <span className="text-[9px] text-zinc-500 font-medium">Click to see next pin</span>}
                          </div>
                          <p className="text-[11px] text-zinc-600 dark:text-zinc-300 truncate mt-0.5">{currentPin.text}</p>
                        </div>
                      </div>
                      {activeChannel.creatorId === user.uid && (
                        <button 
                          type="button" 
                          onClick={() => handleUnpinMessage(currentPin.id)}
                          className="p-1 rounded-full bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 text-zinc-400 hover:text-zinc-600 transition ml-2 shrink-0"
                          title="Unpin Message"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      )}
                    </div>
                    );
                  })()}
"""
content = content.replace(old_channel_pin_render.strip(), new_channel_pin_render.strip())

# 5. Fix popup "Pin/Unpin" check
content = content.replace("activeChannel?.pinnedMessage?.id === msg.id", "((activeChannel?.pinnedMessages || []).some((p: any) => p.id === msg.id) || activeChannel?.pinnedMessage?.id === msg.id)")

with open('pages/Messages.tsx', 'w') as f:
    f.write(content)

print("Messages.tsx patched for multiple pins")
