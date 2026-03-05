/**
 * RefreshContext – Global refresh trigger
 * =========================================
 * Provides a way for the TopBar Refresh button to trigger
 * data re-fetch in any page that subscribes to it.
 */

import { createContext, useContext, useState, useCallback, type ReactNode } from "react";

interface RefreshContextType {
    /** Increment counter to trigger refresh in consumers */
    refreshKey: number;
    /** Call this to trigger a global refresh */
    triggerRefresh: () => void;
}

const RefreshContext = createContext<RefreshContextType>({
    refreshKey: 0,
    triggerRefresh: () => { },
});

export function RefreshProvider({ children }: { children: ReactNode }) {
    const [refreshKey, setRefreshKey] = useState(0);

    const triggerRefresh = useCallback(() => {
        setRefreshKey((k) => k + 1);
    }, []);

    return (
        <RefreshContext.Provider value={{ refreshKey, triggerRefresh }}>
            {children}
        </RefreshContext.Provider>
    );
}

export function useRefresh() {
    return useContext(RefreshContext);
}
