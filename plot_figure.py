import numpy as np
import os
from Config import DynamicsConfig
from utils import myplot, Numpy2Torch
import Dynamics
S_DIM = 4
A_DIM = 1


def plot_comparison(simu_dir, methods):
    '''
    Plot comparison figure among ADP, MPC & open-loop solution.
    Trajectory, tracking error and control signal plot

    Parameters
    ----------
    picture_dir: string
        location of figure saved.

    '''
    num_methods = len(methods)
    picture_dir = simu_dir + "/Figures"
    config = DynamicsConfig()
    trajectory_data = []
    dy = Dynamics.VehicleDynamics()
    if os.path.exists(os.path.join(simu_dir, 'structured_MPC_state.txt')) == 0:
        print('No comparison state data!')
    else:
        if 'MPC' in methods:
            mpc_state = np.loadtxt(os.path.join(simu_dir, 'structured_MPC_state.txt'))
            mpc_trajectory = (mpc_state[:, 4], mpc_state[:, 0])
            trajectory_data.append(mpc_trajectory)
        if 'ADP' in methods:
            adp_state = np.loadtxt(os.path.join(simu_dir, 'ADP_state.txt'))
            adp_trajectory = (adp_state[:, 4], adp_state[:, 0])
            trajectory_data.append(adp_trajectory)
        if 'OP' in methods:
            open_loop_state = np.loadtxt(os.path.join(simu_dir, 'Open_loop_state.txt'))
            open_loop_trajectory = (open_loop_state[:, 4], open_loop_state[:, 0])
            trajectory_data.append(open_loop_trajectory)
        myplot(trajectory_data, num_methods, "xy",
               fname=os.path.join(picture_dir, 'trajectory.png'),
               xlabel="longitudinal position [m]",
               ylabel="Lateral position [m]",
               legend=methods,
               legend_loc="lower left"
               )

        heading_angle = []
        if 'MPC' in methods:
            mpc_state = np.loadtxt(os.path.join(simu_dir, 'structured_MPC_state.txt'))
            mpc_trajectory = (mpc_state[:, 4], 180 / np.pi * mpc_state[:, 2])
            heading_angle.append(mpc_trajectory)
        if 'ADP' in methods:
            adp_state = np.loadtxt(os.path.join(simu_dir, 'ADP_state.txt'))
            adp_trajectory = (adp_state[:, 4], 180 / np.pi * adp_state[:, 2])
            heading_angle.append(adp_trajectory)
        if 'OP' in methods:
            open_loop_state = np.loadtxt(os.path.join(simu_dir, 'Open_loop_state.txt'))
            open_loop_trajectory = (open_loop_state[:, 4], open_loop_state[:, 2])
            heading_angle.append(open_loop_trajectory)
        myplot(heading_angle, num_methods, "xy",
               fname=os.path.join(picture_dir, 'trajectory_heading_angle.png'),
               xlabel="longitudinal position [m]",
               ylabel="Heading angle [degree]",
               legend=methods,
               legend_loc="lower left"
               )

        error_data = []
        print('\nMAX TRACKING ERROR:')
        print(' MAX LATERAL POSITION ERROR:')
        if 'MPC' in methods:
            mpc_ref = dy.reference_trajectory(Numpy2Torch(mpc_state[:, 4], mpc_state[:, 4].shape)).numpy()
            mpc_error = (mpc_state[:, 4], mpc_state[:, 0] - mpc_ref[:, 0])
            print('  Max MPC lateral error: {:0.3E}m'.format(float(max(abs(mpc_state[:, 0] - mpc_ref[:, 0])))))
            error_data.append(mpc_error)
        if 'ADP' in methods:
            adp_ref = dy.reference_trajectory(Numpy2Torch(adp_state[:, 4], adp_state[:, 4].shape)).numpy()
            adp_error = (adp_state[:, 4], adp_state[:, 0] - adp_ref[:, 0])
            print('  Max ADP lateral error: {:0.3E}m'.format(float(max(abs(adp_state[:, 0] - adp_ref[:, 0])))))
            error_data.append(adp_error)
        if 'OP' in methods:
            open_loop_error = (open_loop_state[:, 4], open_loop_state[:, 0] - config.a_curve * np.sin(config.k_curve * open_loop_state[:, 4]))
            error_data.append(open_loop_error)
        myplot(error_data, num_methods, "xy",
               fname=os.path.join(picture_dir, 'trajectory_error.png'),
               xlabel="longitudinal position error [m]",
               ylabel="Lateral position [m]",
               legend=methods,
               legend_loc="upper left"
               )

        # mpc_error = (mpc_state[:, 4], mpc_state[:, 0] - config.a_curve * np.sin(config.k_curve * mpc_state[:, 4]))
        # open_loop_error =  (open_loop_state[:, 4], open_loop_state[:, 0] - config.a_curve * np.sin(config.k_curve * open_loop_state[:, 4]))
        # adp_error = (adp_state[:, 4], 1 * (adp_state[:, 0] - config.a_curve * np.sin(config.k_curve * adp_state[:, 4]))) # TODO: safe delete

        #error_data = [mpc_error, adp_error, open_loop_error]
        # myplot(error_data, 3, "xy",
        #        fname=os.path.join(picture_dir,'trajectory_error.png'),
        #        xlabel="longitudinal position [m]",
        #        ylabel="Lateral position error [m]",
        #        legend=["MPC", "ADP", "Open-loop"],
        #        legend_loc="lower left"
        #        )


        psi_error_data = []
        print(' MAX YAW ANGLE ERROR:')
        if 'MPC' in methods:
            mpc_psi_error = (mpc_state[:, 4], 180 / np.pi * (mpc_state[:, 2] - mpc_ref[:, 2]))
            print('  MPC: {:0.3E} degree'.format(float(max(abs(180 / np.pi * (mpc_state[:, 2] - mpc_ref[:, 2]))))) )
            psi_error_data.append(mpc_psi_error)
        if 'ADP' in methods:
            adp_psi_error = (adp_state[:, 4], 180 / np.pi * (adp_state[:, 2] - adp_ref[:, 2]))
            print('  ADP: {:0.3E} degree'.format(float(max(abs(180 / np.pi * (adp_state[:, 2] - adp_ref[:, 2]))))) )
            psi_error_data.append(adp_psi_error)
        if 'OP' in methods:
            open_loop_psi_error = (open_loop_state[:, 4], 180 / np.pi * (open_loop_state[:, 2] -
                               np.arctan(config.a_curve * config.k_curve * np.cos(config.k_curve * open_loop_state[:, 4]))))
            psi_error_data.append(open_loop_psi_error)

        myplot(psi_error_data, num_methods , "xy",
               fname=os.path.join(picture_dir, 'head_angle_error.png'),
               xlabel="longitudinal position [m]",
               ylabel="head angle error [degree]",
               legend=["MPC", "ADP", "Open-loop"],
               legend_loc="lower left"
               )



        control_plot_data = []
        if 'MPC' in methods:
            mpc_control = np.loadtxt(os.path.join(simu_dir, 'structured_MPC_control.txt'))
            mpc_control_tuple = (mpc_state[1:, 4], 180 / np.pi * mpc_control)
            control_plot_data.append(mpc_control_tuple)
        if 'ADP' in methods:
            adp_control = np.loadtxt(os.path.join(simu_dir, 'ADP_control.txt'))
            adp_control_tuple = (adp_state[1:, 4], 180 / np.pi * adp_control)
            control_plot_data.append(adp_control_tuple)
        if 'OP' in methods:
            open_loop_control = np.loadtxt(os.path.join(simu_dir, 'Open_loop_control.txt'))
            open_loop_control_tuple = (open_loop_state[1:, 4], 180 / np.pi * open_loop_control)
            control_plot_data.append(open_loop_control_tuple)

        myplot(control_plot_data, 3, "xy",
               fname=os.path.join(picture_dir, 'control.png'),
               xlabel="longitudinal position [m]",
               ylabel="steering angle [degree]",
               legend=["MPC", "ADP", "Open-loop"],
               legend_loc="upper left"
               )

        if 'OP' in methods:

            y_avs_error = []
            for [i, d] in enumerate(error_data):
                y_avs_error.append(np.mean(np.abs(d[1])))
            print("Tracking error of lateral position:")
            print("MPC:{:.3e} | ".format(y_avs_error[0]) +
                  "ADP:{:.3e} | ".format(y_avs_error[1]) +
                  "Open-loop:{:.3e} | ".format(y_avs_error[2]))

            psi_avs_error = []
            for [i, d] in enumerate(psi_error_data):
                psi_avs_error.append(np.mean(np.abs(d[1])))
            print("Tracking error of heading angle:")
            print("MPC:{:.3e} | ".format(psi_avs_error[0]) +
                  "ADP:{:.3e} | ".format(psi_avs_error[1]) +
                  "Open-loop:{:.3e} | ".format(psi_avs_error[2]))

            mpc_control_error = mpc_control - open_loop_control
            adp_control_error = adp_control - open_loop_control
            print("Control error:")
            print("MPC:{:.3e} | ".format(np.mean(np.abs(mpc_control_error))) +
                  "ADP:{:.3e} | ".format(np.mean(np.abs(adp_control_error))))

def plot_loss_decent_compare(comparison_dir):
    fs_step = ["10","20","30"]
    value_loss = []
    policy_loss = []
    p_scatter_data = []
    v_scatter_data = []
    for [i,fs] in enumerate(fs_step):
        value_np = "value_loss_" + fs + ".txt"
        policy_np = "policy_loss_" + fs + ".txt"
        value_loss.append(np.loadtxt(os.path.join(comparison_dir, value_np)))
        policy_loss.append(np.loadtxt(os.path.join(comparison_dir, policy_np)))
        p_scatter_data.append((range(len(policy_loss[i])), policy_loss[i]))
        v_scatter_data.append((range(len(value_loss[i])), np.log10(value_loss[i])))
    myplot(v_scatter_data,3,"scatter",
           fname=(os.path.join(comparison_dir, "p_loss.png")),
           xlabel="iteration",
           ylabel="log value loss",
           legend=["10 steps","20 steps","30 steps"],
           xlim=[0, 5000],
           ylim=[0, 3]
           )

def plot_loss_decent(log_dir):
    value_loss = np.loadtxt(os.path.join(log_dir, "value_loss.txt"))
    policy_loss = np.loadtxt(os.path.join(log_dir, "policy_loss.txt"))
    value_loss_tuple = (range(len(value_loss)), np.log10(value_loss))
    policy_loss_tuple = (range(len(policy_loss)), np.log10(policy_loss))
    loss = [value_loss_tuple, policy_loss_tuple]
    myplot(loss, 2, "scatter",
           fname=(os.path.join(log_dir, "loss.png")),
           xlabel="iteration",
           ylabel="log value loss",
           legend=["PEV loss", "PIM loss"],
           xlim=[0, 5000],
           ylim=[-1, 3]
           )


def adp_simulation_plot(simu_dir):
    '''
    Simulate and plot trajectory and control after ADP training algorithm.

    Parameters
    ----------
    simu_dir: string
        location of data and figures saved.

    '''
    state_history = np.loadtxt(os.path.join(simu_dir, 'ADP_state.txt'))
    control_history = np.loadtxt(os.path.join(simu_dir, 'ADP_control.txt'))
    trajectory = (state_history[:, -1], state_history[:, 0])
    figures_dir = simu_dir + "/Figures"
    os.makedirs(figures_dir, exist_ok=True)
    myplot(trajectory, 1, "xy",
           fname=os.path.join(figures_dir, 'adp_trajectory.png'),
           xlabel="longitudinal position [m]",
           ylabel="Lateral position [m]",
           legend=["trajectory"],
           legend_loc="upper left"
           )
    u_lat = (state_history[:, -1], state_history[:, 1])
    psi =(state_history[:, -1], state_history[:, 2])
    omega = (state_history[:, -1], state_history[:, 3])
    data = [u_lat, psi, omega]
    legend=["$u_{lat}$", "$\psi$", "$\omega$"]
    myplot(data, 3, "xy",
           fname=os.path.join(figures_dir, 'adp_other_state.png'),
           xlabel="longitudinal position [m]",
           legend=legend
           )
    control_history_plot = (state_history[1:, -1], 180 / np.pi * control_history)
    myplot(control_history_plot, 1, "xy",
           fname=os.path.join(figures_dir, 'adp_control.png'),
           xlabel="longitudinal position [m]",
           ylabel="steering angle [degree]"
           )


