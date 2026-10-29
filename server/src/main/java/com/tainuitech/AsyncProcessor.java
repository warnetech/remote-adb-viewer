package com.tainuitech;

public interface AsyncProcessor {
    interface TerminationListener {
        /**
         * Notify processor termination
         *
         * @param fatalError {@code true} if this must cause the termination of the whole tainuitech-server.
         */
        void onTerminated(boolean fatalError);
    }

    void start(TerminationListener listener);

    void stop();

    void join() throws InterruptedException;
}
