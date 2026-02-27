
import { createClient } from '@supabase/supabase-js';
import * as dotenv from 'dotenv';
import { resolve } from 'path';

// Load .env from project root
dotenv.config({ path: resolve(process.cwd(), '.env') });

const supabaseUrl = process.env.VITE_SUPABASE_URL;
const supabaseAnonKey = process.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
    console.error("Missing VITE_SUPABASE_URL or VITE_SUPABASE_ANON_KEY in .env");
    process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseAnonKey);

async function seedUsers() {
    const users = [
        { email: 'admin@elfaideias.com', password: 'password123', role: 'admin', name: 'Admin User' },
        { email: 'colab@elfaideias.com', password: 'password123', role: 'collaborator', name: 'Collaborator User' },
    ];

    console.log("Seeding users via Public Sign Up...");

    for (const u of users) {
        console.log(`-- Processing ${u.email}...`);

        // 1. Sign Up
        const { data, error } = await supabase.auth.signUp({
            email: u.email,
            password: u.password,
            options: {
                data: { name: u.name, avatar_url: '' }
            }
        });

        if (error) {
            console.log(`Error/Info: ${error.message}`);
        } else if (data.user) {
            console.log(`User created: ${data.user.id}`);
        }
    }
}

seedUsers();
