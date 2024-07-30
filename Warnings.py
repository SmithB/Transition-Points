def generate_warnings(transition_errors, significant_rgts_under_thresh):
    with open('assets/warnings.txt', 'w') as file:
        file.write('Errors:\n')
        for error in transition_errors:
            file.write(f'RGT: {error} \n')
        file.write("\n")

        file.write('Warnings:\n\n')
        file.write('RGTs where large segments under threshold were skipped:\n')
        for rgt in significant_rgts_under_thresh:
            file.write(f'RGT: {rgt}\n')

        file.write('RGTs where there are multiple Transition Points in a 1500 km distance:\n')

