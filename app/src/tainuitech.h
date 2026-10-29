#ifndef TAINUITECH_H
#define TAINUITECH_H

#include "common.h"

#include "options.h"

enum tainuitech_exit_code {
    // Normal program termination
    TAINUITECH_EXIT_SUCCESS,

    // No connection could be established
    TAINUITECH_EXIT_FAILURE,

    // Device was disconnected while running
    TAINUITECH_EXIT_DISCONNECTED,
};

enum tainuitech_exit_code
tainuitech(struct tainuitech_options *options);

#endif
