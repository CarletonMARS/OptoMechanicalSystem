% Normalized dB scale plot
%% Script to plot angular response for different wavelengths
clear all; clc; close all;

%% ======== EDITABLE VARIABLES ======== %%
folder_path = 'Data'; % Folder containing angle-based CSV files
start_angle = 26;
stop_angle = 30.2; 
step_size = 0.1;

lambda = 1525:5:1560;


% Column indices in CSV files
wavelength_col = 1; % Column containing wavelength values
current_col = 2;    % Column containing current values

%% ======== PROCESSING ======== %%
% Generate angle values
angles = start_angle:step_size:stop_angle;
num_angles = length(angles);


% Process each angle file
for waves = 1:length(lambda)
    for i = 1:num_angles
        % Construct filename based on angle
        angle_val = angles(i);
        filename = fullfile(folder_path, sprintf('%.1f.csv', angle_val));
        
        % Check if file exists
        if exist(filename, 'file')
            % Read data
            data = readmatrix(filename);
            currents_all(i) = data(waves*5+1,2);
        else
            fprintf('Warning: File not found: %s\n', filename);
            currents(:, i) = NaN; % Mark as missing data
        end
    end
    [~, idx] = max(currents_all);
    max_angle(waves) = angles(idx);
end

figure(5);
hold on;
plot(lambda,max_angle,'o')
plot(lambda, rad2deg(asin(0.0003*lambda))+0.41)
